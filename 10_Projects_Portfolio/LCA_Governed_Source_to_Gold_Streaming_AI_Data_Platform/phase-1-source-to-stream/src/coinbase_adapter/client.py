"""Resilient Coinbase WebSocket connection loop."""

import asyncio
import json
import logging
import random
from typing import Any, Callable, Dict, List, Optional

import websockets

from .config import AdapterConfig, SUPPORTED_CHANNELS
from .handler import MessageHandler, Outcome


LOGGER = logging.getLogger(__name__)


class StaleHeartbeatError(RuntimeError):
    """Raised when a live Coinbase heartbeat is missing or becomes stale."""


def subscription_messages(config: AdapterConfig) -> List[Dict[str, Any]]:
    return [
        {
            "type": "subscribe",
            "product_ids": list(config.products),
            "channel": channel,
        }
        for channel in SUPPORTED_CHANNELS
    ]


class CoinbaseWebSocketClient:
    def __init__(
        self,
        config: AdapterConfig,
        handler: MessageHandler,
        max_market_messages: Optional[int] = None,
        sleep: Callable[[float], Any] = asyncio.sleep,
        random_value: Callable[[], float] = random.random,
    ) -> None:
        if max_market_messages is not None and max_market_messages <= 0:
            raise ValueError("max_market_messages must be positive when provided")
        self.config = config
        self.handler = handler
        self.max_market_messages = max_market_messages
        self._sleep = sleep
        self._random_value = random_value

    async def run(self) -> None:
        attempt = 0
        while True:
            try:
                completed = await self._consume_connection()
                if completed:
                    return
                attempt = 0
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # Connection failures are retried and measured by logs.
                delay = self._backoff_seconds(attempt)
                LOGGER.warning(
                    "coinbase_connection_retry",
                    extra={
                        "error_type": type(exc).__name__,
                        "retry_attempt": attempt + 1,
                        "retry_delay_seconds": round(delay, 3),
                    },
                )
                attempt += 1
                await self._sleep(delay)

    async def _consume_connection(self) -> bool:
        LOGGER.info("coinbase_connecting", extra={"endpoint": self.config.endpoint})
        async with websockets.connect(
            self.config.endpoint,
            ping_interval=20,
            ping_timeout=20,
            max_size=self.config.max_message_bytes,
        ) as websocket:
            for message in subscription_messages(self.config):
                await websocket.send(json.dumps(message, separators=(",", ":")))
            connection_started = asyncio.get_running_loop().time()
            LOGGER.info(
                "coinbase_subscribed",
                extra={
                    "channels": list(SUPPORTED_CHANNELS),
                    "products": list(self.config.products),
                },
            )

            while True:
                heartbeat_age = self.handler.heartbeat_age_seconds()
                if heartbeat_age is None:
                    heartbeat_age = asyncio.get_running_loop().time() - connection_started
                remaining_heartbeat_seconds = max(
                    0.1, self.config.stale_heartbeat_seconds - heartbeat_age
                )
                try:
                    raw_message = await asyncio.wait_for(
                        websocket.recv(), timeout=remaining_heartbeat_seconds
                    )
                except asyncio.TimeoutError as exc:
                    raise StaleHeartbeatError(
                        "No Coinbase message arrived within the heartbeat threshold"
                    ) from exc

                if isinstance(raw_message, bytes):
                    try:
                        raw_message = raw_message.decode("utf-8")
                    except UnicodeDecodeError:
                        raw_message = ""

                outcome = await self.handler.handle(raw_message)
                heartbeat_age = self.handler.heartbeat_age_seconds()
                if (
                    outcome != Outcome.HEARTBEAT_OBSERVED
                    and heartbeat_age is None
                    and asyncio.get_running_loop().time() - connection_started
                    >= self.config.stale_heartbeat_seconds
                ):
                    raise StaleHeartbeatError("Coinbase heartbeat was not observed")
                if (
                    outcome != Outcome.HEARTBEAT_OBSERVED
                    and heartbeat_age is not None
                    and heartbeat_age >= self.config.stale_heartbeat_seconds
                ):
                    raise StaleHeartbeatError("Coinbase heartbeat became stale")
                if (
                    outcome == Outcome.MARKET_PUBLISHED
                    and self.max_market_messages is not None
                    and self.handler.metrics.market_messages_published >= self.max_market_messages
                ):
                    return True

    def _backoff_seconds(self, attempt: int) -> float:
        base = min(
            self.config.reconnect_max_seconds,
            self.config.reconnect_initial_seconds * (2**attempt),
        )
        jitter_multiplier = 0.5 + (self._random_value() * 0.5)
        return base * jitter_multiplier
