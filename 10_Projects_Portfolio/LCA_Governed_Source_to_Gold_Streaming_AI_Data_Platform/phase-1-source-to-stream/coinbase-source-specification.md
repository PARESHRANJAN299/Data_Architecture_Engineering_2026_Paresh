# Coinbase Advanced Trade Source Specification

**Decision:** Locked for Phase 1
**Owner:** Paresh Ranjan Rout

## Connection profile

| Property | Value |
|---|---|
| Endpoint | `wss://advanced-trade-ws.coinbase.com` |
| Business channel | `market_trades` |
| Health channel | `heartbeats` |
| Products | `BTC-USD`, `ETH-USD` |
| Initial authentication | None for public market-data channels |
| Runtime | One ECS Fargate service, desired count determined during failure testing |
| Configuration | Environment/AppConfig for endpoint, channels and product allowlist; no secret in Git |

The adapter must send subscriptions immediately after connection, monitor heartbeat age, reconnect with capped exponential backoff and jitter, and resubscribe after every reconnect.

Send one subscription message per channel:

```json
{
  "type": "subscribe",
  "product_ids": ["BTC-USD", "ETH-USD"],
  "channel": "market_trades"
}
```

```json
{
  "type": "subscribe",
  "product_ids": ["BTC-USD", "ETH-USD"],
  "channel": "heartbeats"
}
```

## Message handling

1. Validate the WebSocket envelope and supported channel.
2. Record source message timestamp, receive timestamp, channel, and `sequence_num`.
3. For `market_trades`, iterate through every trade in every event group.
4. Produce one canonical event per trade.
5. Update heartbeat and connection metrics without publishing heartbeats as business events.
6. Ignore unknown message types safely while emitting a compatibility metric and sampled diagnostic metadata.

## Canonical mapping

| Canonical field | Coinbase source or rule |
|---|---|
| `event_id` | `coinbase.market_trade.{product_id}.{trade_id}` |
| `event_type` | `market.trade` |
| `event_source` | `coinbase.advanced_trade` |
| `schema_name` | `market-trade` |
| `schema_version` | Contract version, initially `1.0.0` |
| `source_event_time` | Trade `time` |
| `ingestion_time` | Adapter UTC receipt time |
| `partition_key` | `coinbase.advanced_trade#{product_id}` |
| `classification` | `public` |
| `payload.product_id` | Coinbase `product_id` |
| `payload.trade_id` | Coinbase `trade_id` |
| `payload.price` | Coinbase decimal string; do not convert through floating point |
| `payload.size` | Coinbase decimal string; do not convert through floating point |
| `payload.side` | Coinbase maker side normalized to lowercase |
| `payload.source_sequence_num` | WebSocket envelope `sequence_num` |
| `payload.source_message_timestamp` | WebSocket envelope `timestamp` |

## Ordering, duplication and gaps

- Kinesis ordering is scoped to one Coinbase product.
- Producer retries can create duplicates; downstream consumers remain idempotent by `event_id`.
- Persist the last observed sequence per connection/channel where it improves diagnosis.
- Do not treat `sequence_num` alone as proof of business completeness until live tests confirm its scope and reset behavior across reconnects.
- A detected gap starts best-effort REST recovery and always produces a gap report.
- If source history cannot prove recovery, mark the gap unrecovered; never silently infer completeness.

## Explicitly deferred

- authenticated user/order channels;
- order placement or trading;
- `level2` order-book reconstruction;
- additional products before partition and cost evidence exists;
- claims of guaranteed Coinbase historical replay.
