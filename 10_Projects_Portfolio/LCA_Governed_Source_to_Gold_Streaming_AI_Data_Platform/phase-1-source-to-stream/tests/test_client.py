import unittest

from coinbase_adapter.client import CoinbaseWebSocketClient, subscription_messages
from coinbase_adapter.config import AdapterConfig


class SubscriptionTest(unittest.TestCase):
    def test_one_subscription_message_is_created_per_channel(self) -> None:
        messages = subscription_messages(AdapterConfig())

        self.assertEqual(2, len(messages))
        self.assertEqual(["market_trades", "heartbeats"], [m["channel"] for m in messages])
        self.assertTrue(all(m["product_ids"] == ["BTC-USD", "ETH-USD"] for m in messages))

    def test_backoff_is_capped_and_jittered(self) -> None:
        client = CoinbaseWebSocketClient(
            AdapterConfig(reconnect_initial_seconds=2, reconnect_max_seconds=10),
            handler=object(),  # type: ignore[arg-type]
            random_value=lambda: 0.0,
        )

        self.assertEqual(1.0, client._backoff_seconds(0))
        self.assertEqual(5.0, client._backoff_seconds(99))


if __name__ == "__main__":
    unittest.main()
