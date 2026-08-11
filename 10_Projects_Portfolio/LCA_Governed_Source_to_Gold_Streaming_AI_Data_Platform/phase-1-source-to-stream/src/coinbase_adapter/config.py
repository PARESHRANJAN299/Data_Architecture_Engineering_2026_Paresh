"""Validated runtime configuration for the source adapter."""

from dataclasses import dataclass
import os
from typing import Mapping, Optional, Tuple


DEFAULT_ENDPOINT = "wss://advanced-trade-ws.coinbase.com"
DEFAULT_PRODUCTS = ("BTC-USD", "ETH-USD")
SUPPORTED_CHANNELS = ("market_trades", "heartbeats")


def _csv(value: str) -> Tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class AdapterConfig:
    endpoint: str = DEFAULT_ENDPOINT
    products: Tuple[str, ...] = DEFAULT_PRODUCTS
    stale_heartbeat_seconds: float = 10.0
    reconnect_initial_seconds: float = 1.0
    reconnect_max_seconds: float = 30.0
    max_message_bytes: int = 1_048_576

    def __post_init__(self) -> None:
        if not self.endpoint.startswith("wss://"):
            raise ValueError("COINBASE_WS_ENDPOINT must use wss://")
        if not self.products:
            raise ValueError("At least one Coinbase product is required")
        if len(set(self.products)) != len(self.products):
            raise ValueError("Coinbase products must be unique")
        if self.stale_heartbeat_seconds <= 0:
            raise ValueError("stale_heartbeat_seconds must be positive")
        if self.reconnect_initial_seconds <= 0:
            raise ValueError("reconnect_initial_seconds must be positive")
        if self.reconnect_max_seconds < self.reconnect_initial_seconds:
            raise ValueError("reconnect_max_seconds must be >= reconnect_initial_seconds")
        if self.max_message_bytes <= 0:
            raise ValueError("max_message_bytes must be positive")

    @property
    def partition_key(self) -> str:
        return "coinbase.advanced_trade#" + "+".join(sorted(self.products))

    @classmethod
    def from_env(cls, environ: Optional[Mapping[str, str]] = None) -> "AdapterConfig":
        values = os.environ if environ is None else environ
        products = _csv(values.get("COINBASE_PRODUCTS", ",".join(DEFAULT_PRODUCTS)))
        return cls(
            endpoint=values.get("COINBASE_WS_ENDPOINT", DEFAULT_ENDPOINT),
            products=products,
            stale_heartbeat_seconds=float(values.get("STALE_HEARTBEAT_SECONDS", "10")),
            reconnect_initial_seconds=float(values.get("RECONNECT_INITIAL_SECONDS", "1")),
            reconnect_max_seconds=float(values.get("RECONNECT_MAX_SECONDS", "30")),
            max_message_bytes=int(values.get("MAX_MESSAGE_BYTES", "1048576")),
        )
