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
from .sinks import JsonlQuarantineSink, JsonlRawMessageSink


LOGGER = logging.getLogger(__name__)


def _arguments(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture unchanged Coinbase market-trade messages")
    parser.add_argument("--output", required=True, type=Path, help="Development JSONL raw sink")
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


async def _run(args: argparse.Namespace) -> None:
    config = AdapterConfig.from_env()
    quarantine_path = args.quarantine or args.output.with_name("quarantine.jsonl")
    handler = MessageHandler(
        raw_sink=JsonlRawMessageSink(args.output),
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
