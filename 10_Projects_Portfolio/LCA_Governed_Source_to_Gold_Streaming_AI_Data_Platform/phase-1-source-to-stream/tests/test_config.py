import unittest

from coinbase_adapter.config import AdapterConfig


class AdapterConfigTest(unittest.TestCase):
    def test_defaults_lock_the_approved_source(self) -> None:
        config = AdapterConfig.from_env({})

        self.assertEqual("wss://advanced-trade-ws.coinbase.com", config.endpoint)
        self.assertEqual(("BTC-USD", "ETH-USD"), config.products)
        self.assertEqual(
            "coinbase.advanced_trade#BTC-USD+ETH-USD", config.partition_key
        )

    def test_environment_products_are_trimmed(self) -> None:
        config = AdapterConfig.from_env({"COINBASE_PRODUCTS": "ETH-USD, BTC-USD"})

        self.assertEqual(("ETH-USD", "BTC-USD"), config.products)

    def test_plaintext_endpoint_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "wss://"):
            AdapterConfig(endpoint="ws://unsafe.example")


if __name__ == "__main__":
    unittest.main()
