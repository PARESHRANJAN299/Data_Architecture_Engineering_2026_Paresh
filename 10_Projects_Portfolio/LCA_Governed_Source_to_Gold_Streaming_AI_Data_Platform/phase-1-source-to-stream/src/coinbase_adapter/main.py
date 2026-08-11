"""Command-line entry point for the local Phase 1 adapter."""

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Optional, Sequence

from .client import CoinbaseWebSocketClient
from .config import AdapterConfig
from .handler import MessageHandler
from .sinks import (
    JsonlQuarantineSink,
    JsonlRawMessageSink,
    KinesisRawMessageSink,
    RawMessageSink,
)


LOGGER = logging.getLogger(__name__)


def _arguments(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture unchanged Coinbase market-trade messages")
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--output", type=Path, help="Development JSONL raw sink")
    destination.add_argument(
        "--kinesis-stream",
        help="Kinesis stream receiving one unchanged source message per record",
    )
    parser.add_argument(
        "--quarantine",
        type=Path,
        help="Development quarantine JSONL path; defaults beside --output",
    )
    parser.add_argument(
        "--max-market-messages",
        type=int,
        help="Exit successfully after this many market-trade messages",
    )
    return parser.parse_args(argv)


def _raw_sink(args: argparse.Namespace) -> RawMessageSink:
    if args.kinesis_stream:
        import boto3

        return KinesisRawMessageSink(
            stream_name=args.kinesis_stream,
            client=boto3.client("kinesis"),
        )
    return JsonlRawMessageSink(args.output)


async def _run(args: argparse.Namespace) -> None:
    config = AdapterConfig.from_env()
    quarantine_path = args.quarantine
    if quarantine_path is None:
        quarantine_path = (
            args.output.with_name("quarantine.jsonl")
            if args.output
            else Path("/tmp/coinbase-quarantine.jsonl")
        )
    handler = MessageHandler(
        raw_sink=_raw_sink(args),
        quarantine_sink=JsonlQuarantineSink(quarantine_path),
        partition_key=config.partition_key,
    )
    client = CoinbaseWebSocketClient(
        config=config,
        handler=handler,
        max_market_messages=args.max_market_messages,
    )
    try:
        await client.run()
    finally:
        LOGGER.info(
            "adapter_final_metrics %s",
            json.dumps(handler.metrics.as_dict(), sort_keys=True),
        )


def main(argv: Optional[Sequence[str]] = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    asyncio.run(_run(_arguments(argv)))


if __name__ == "__main__":
    main()
