from pathlib import Path
import unittest

from coinbase_adapter.handler import MessageHandler, Outcome


FIXTURES = Path(__file__).parent / "fixtures"


class MemoryRawSink:
    def __init__(self) -> None:
        self.records = []

    async def publish(self, raw_message: str, partition_key: str) -> None:
        self.records.append((raw_message, partition_key))


class MemoryQuarantineSink:
    def __init__(self) -> None:
        self.records = []

    async def quarantine(self, raw_message: str, reason: str) -> None:
        self.records.append((raw_message, reason))


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8").strip()


class MessageHandlerTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.raw_sink = MemoryRawSink()
        self.quarantine_sink = MemoryQuarantineSink()
        self.clock = 100.0
        self.handler = MessageHandler(
            self.raw_sink,
            self.quarantine_sink,
            "coinbase.advanced_trade#BTC-USD+ETH-USD",
            monotonic=lambda: self.clock,
        )

    async def test_single_trade_message_is_published_byte_for_byte(self) -> None:
        raw = fixture("market-trades-single.json")

        outcome = await self.handler.handle(raw)

        self.assertEqual(Outcome.MARKET_PUBLISHED, outcome)
        self.assertEqual(raw, self.raw_sink.records[0][0])
        self.assertEqual(1, self.handler.metrics.market_messages_published)

    async def test_multi_trade_message_stays_one_raw_record(self) -> None:
        raw = fixture("market-trades-multiple.json")

        await self.handler.handle(raw)

        self.assertEqual(1, len(self.raw_sink.records))
        self.assertEqual(raw, self.raw_sink.records[0][0])

    async def test_heartbeat_updates_health_but_is_not_published(self) -> None:
        outcome = await self.handler.handle(fixture("heartbeat.json"))

        self.assertEqual(Outcome.HEARTBEAT_OBSERVED, outcome)
        self.assertEqual([], self.raw_sink.records)
        self.assertEqual(0.0, self.handler.heartbeat_age_seconds(now=100.0))

        self.clock = 106.5
        self.assertEqual(6.5, self.handler.heartbeat_age_seconds())

    async def test_invalid_json_is_quarantined(self) -> None:
        outcome = await self.handler.handle("{not-json")

        self.assertEqual(Outcome.QUARANTINED, outcome)
        self.assertEqual("invalid_json", self.quarantine_sink.records[0][1])
        self.assertEqual([], self.raw_sink.records)

    async def test_unsupported_channel_is_ignored(self) -> None:
        outcome = await self.handler.handle('{"channel":"subscriptions"}')

        self.assertEqual(Outcome.UNSUPPORTED_IGNORED, outcome)
        self.assertEqual([], self.quarantine_sink.records)

    async def test_interleaved_control_sequence_does_not_create_false_gap(self) -> None:
        market = fixture("market-trades-single.json")
        control = '{"channel":"subscriptions","sequence_num":103}'
        heartbeat = fixture("heartbeat.json").replace(
            '"sequence_num":101', '"sequence_num":104'
        )

        await self.handler.handle(market)
        await self.handler.handle(control)
        await self.handler.handle(heartbeat)

        self.assertEqual(0, self.handler.metrics.sequence_gaps)

    async def test_sequence_gap_is_measured_without_changing_payload(self) -> None:
        first = fixture("market-trades-single.json")
        second = fixture("market-trades-multiple.json").replace(
            '"sequence_num":103', '"sequence_num":105'
        )

        await self.handler.handle(first)
        await self.handler.handle(second)

        self.assertEqual(2, self.handler.metrics.sequence_gaps)
        self.assertEqual(second, self.raw_sink.records[1][0])


if __name__ == "__main__":
    unittest.main()
