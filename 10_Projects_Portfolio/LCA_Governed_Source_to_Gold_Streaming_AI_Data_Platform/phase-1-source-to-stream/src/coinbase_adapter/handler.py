"""Route Coinbase messages while preserving market-trade payload bytes."""

from dataclasses import dataclass
from enum import Enum
import json
import time
from typing import Any, Callable, Dict, Mapping, Optional

from .sinks import QuarantineSink, RawMessageSink


class Outcome(str, Enum):
    MARKET_PUBLISHED = "market_published"
    HEARTBEAT_OBSERVED = "heartbeat_observed"
    UNSUPPORTED_IGNORED = "unsupported_ignored"
    QUARANTINED = "quarantined"


@dataclass
class AdapterMetrics:
    messages_received: int = 0
    market_messages_published: int = 0
    heartbeats_observed: int = 0
    unsupported_messages: int = 0
    quarantined_messages: int = 0
    sequence_gaps: int = 0
    out_of_order_messages: int = 0

    def as_dict(self) -> Dict[str, int]:
        return {
            "messages_received": self.messages_received,
            "market_messages_published": self.market_messages_published,
            "heartbeats_observed": self.heartbeats_observed,
            "unsupported_messages": self.unsupported_messages,
            "quarantined_messages": self.quarantined_messages,
            "sequence_gaps": self.sequence_gaps,
            "out_of_order_messages": self.out_of_order_messages,
        }


@dataclass
class SequenceTracker:
    last_sequence_num: Optional[int] = None

    def observe(self, sequence_num: int, metrics: AdapterMetrics) -> None:
        previous = self.last_sequence_num
        if previous is not None:
            if sequence_num > previous + 1:
                metrics.sequence_gaps += sequence_num - previous - 1
            elif sequence_num <= previous:
                metrics.out_of_order_messages += 1
        if previous is None or sequence_num > previous:
            self.last_sequence_num = sequence_num


class MessageHandler:
    def __init__(
        self,
        raw_sink: RawMessageSink,
        quarantine_sink: QuarantineSink,
        partition_key: str,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self._raw_sink = raw_sink
        self._quarantine_sink = quarantine_sink
        self._partition_key = partition_key
        self._monotonic = monotonic
        self.metrics = AdapterMetrics()
        self.sequence = SequenceTracker()
        self.last_heartbeat_monotonic: Optional[float] = None

    async def handle(self, raw_message: str) -> Outcome:
        self.metrics.messages_received += 1
        try:
            envelope = json.loads(raw_message)
        except json.JSONDecodeError:
            return await self._quarantine(raw_message, "invalid_json")

        if not isinstance(envelope, Mapping):
            return await self._quarantine(raw_message, "envelope_not_object")

        # Observe every sequenced envelope on this connection before channel routing.
        # This prevents interleaved subscription and heartbeat messages from creating
        # false local gaps; sequence scope remains diagnostic until longer tests pass.
        envelope_sequence = envelope.get("sequence_num")
        if isinstance(envelope_sequence, int) and not isinstance(envelope_sequence, bool):
            self.sequence.observe(envelope_sequence, self.metrics)

        channel = envelope.get("channel")
        if channel not in ("market_trades", "heartbeats"):
            self.metrics.unsupported_messages += 1
            return Outcome.UNSUPPORTED_IGNORED

        reason = self._validate_envelope(envelope)
        if reason is not None:
            return await self._quarantine(raw_message, reason)

        if channel == "heartbeats":
            self.last_heartbeat_monotonic = self._monotonic()
            self.metrics.heartbeats_observed += 1
            return Outcome.HEARTBEAT_OBSERVED

        await self._raw_sink.publish(raw_message, self._partition_key)
        self.metrics.market_messages_published += 1
        return Outcome.MARKET_PUBLISHED

    async def _quarantine(self, raw_message: str, reason: str) -> Outcome:
        await self._quarantine_sink.quarantine(raw_message, reason)
        self.metrics.quarantined_messages += 1
        return Outcome.QUARANTINED

    @staticmethod
    def _validate_envelope(envelope: Mapping[str, Any]) -> Optional[str]:
        if not isinstance(envelope.get("timestamp"), str):
            return "missing_or_invalid_timestamp"
        sequence_num = envelope.get("sequence_num")
        if not isinstance(sequence_num, int) or isinstance(sequence_num, bool):
            return "missing_or_invalid_sequence_num"
        if not isinstance(envelope.get("events"), list):
            return "missing_or_invalid_events"
        return None

    def heartbeat_age_seconds(self, now: Optional[float] = None) -> Optional[float]:
        if self.last_heartbeat_monotonic is None:
            return None
        current = self._monotonic() if now is None else now
        return max(0.0, current - self.last_heartbeat_monotonic)
