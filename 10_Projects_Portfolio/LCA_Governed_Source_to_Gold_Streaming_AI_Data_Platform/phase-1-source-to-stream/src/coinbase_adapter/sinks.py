"""Raw-message and quarantine sinks for local and AWS runtimes."""

import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Protocol


class RawMessageSink(Protocol):
    async def publish(self, raw_message: str, partition_key: str) -> None:
        """Publish the original source message without rewriting it."""


class QuarantineSink(Protocol):
    async def quarantine(self, raw_message: str, reason: str) -> None:
        """Store an unreadable transport payload and a safe reason."""


class KinesisPutRecordClient(Protocol):
    def put_record(self, **kwargs: object) -> object:
        """Write one record using the subset of the boto3 Kinesis client we need."""


async def _append_line(path: Path, value: str) -> None:
    def write() -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(value)
            stream.write("\n")

    await asyncio.to_thread(write)


class JsonlRawMessageSink:
    """Development-only sink that writes one unchanged WebSocket message per line."""

    def __init__(self, path: Path) -> None:
        self.path = path

    async def publish(self, raw_message: str, partition_key: str) -> None:
        del partition_key  # Kinesis uses this value; the local raw file intentionally does not.
        await _append_line(self.path, raw_message)


class KinesisRawMessageSink:
    """Publish one unchanged Coinbase WebSocket message as one Kinesis record."""

    def __init__(
        self,
        stream_name: str,
        client: KinesisPutRecordClient,
        max_record_bytes: int = 1_048_576,
    ) -> None:
        if not stream_name.strip():
            raise ValueError("Kinesis stream name must not be empty")
        if max_record_bytes <= 0:
            raise ValueError("max_record_bytes must be positive")
        self.stream_name = stream_name
        self.client = client
        self.max_record_bytes = max_record_bytes

    async def publish(self, raw_message: str, partition_key: str) -> None:
        if not partition_key:
            raise ValueError("Kinesis partition key must not be empty")

        payload = raw_message.encode("utf-8")
        record_size = len(payload) + len(partition_key.encode("utf-8"))
        if record_size > self.max_record_bytes:
            raise ValueError(
                "Kinesis record exceeds the configured maximum record size"
            )

        await asyncio.to_thread(
            self.client.put_record,
            StreamName=self.stream_name,
            Data=payload,
            PartitionKey=partition_key,
        )


class JsonlQuarantineSink:
    """Development-only quarantine; never emits payload contents to application logs."""

    def __init__(self, path: Path) -> None:
        self.path = path

    async def quarantine(self, raw_message: str, reason: str) -> None:
        record = {
            "quarantined_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
            "raw_message": raw_message,
        }
        await _append_line(self.path, json.dumps(record, separators=(",", ":")))
