import unittest

from coinbase_adapter.sinks import KinesisRawMessageSink


class RecordingKinesisClient:
    def __init__(self, error=None) -> None:
        self.calls = []
        self.error = error

    def put_record(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return {"ShardId": "shardId-000000000000", "SequenceNumber": "123"}


class KinesisRawMessageSinkTest(unittest.IsolatedAsyncioTestCase):
    async def test_publish_preserves_source_bytes_and_targets_exact_stream(self) -> None:
        client = RecordingKinesisClient()
        sink = KinesisRawMessageSink(
            stream_name="lca-coinbase-market-trades-dev",
            client=client,
        )
        raw = '{ "channel": "market_trades", "price": "64321.10" }'
        partition_key = "coinbase.advanced_trade#BTC-USD+ETH-USD"

        await sink.publish(raw, partition_key)

        self.assertEqual(1, len(client.calls))
        self.assertEqual(
            {
                "StreamName": "lca-coinbase-market-trades-dev",
                "Data": raw.encode("utf-8"),
                "PartitionKey": partition_key,
            },
            client.calls[0],
        )

    async def test_one_multi_trade_message_remains_one_kinesis_record(self) -> None:
        client = RecordingKinesisClient()
        sink = KinesisRawMessageSink("lca-coinbase-market-trades-dev", client)
        raw = '{"channel":"market_trades","events":[{"trades":[{"id":"1"},{"id":"2"}]}]}'

        await sink.publish(raw, "coinbase.advanced_trade#BTC-USD+ETH-USD")

        self.assertEqual(1, len(client.calls))
        self.assertEqual(raw.encode("utf-8"), client.calls[0]["Data"])

    async def test_oversized_record_is_rejected_before_aws_call(self) -> None:
        client = RecordingKinesisClient()
        sink = KinesisRawMessageSink(
            "lca-coinbase-market-trades-dev",
            client,
            max_record_bytes=20,
        )

        with self.assertRaisesRegex(ValueError, "maximum record size"):
            await sink.publish("x" * 20, "partition")

        self.assertEqual([], client.calls)

    async def test_aws_client_error_is_not_hidden(self) -> None:
        client = RecordingKinesisClient(error=RuntimeError("simulated throttle"))
        sink = KinesisRawMessageSink("lca-coinbase-market-trades-dev", client)

        with self.assertRaisesRegex(RuntimeError, "simulated throttle"):
            await sink.publish("{}", "partition")


if __name__ == "__main__":
    unittest.main()
