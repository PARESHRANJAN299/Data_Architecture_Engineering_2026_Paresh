"""Local sinks with the same raw-payload boundary later used by Kinesis."""

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
