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
3. For `market_trades`, preserve the complete source message and nested trade arrays unchanged.
4. Publish one raw source message per Kinesis record; do not rename, aggregate or cast business fields.
5. Update heartbeat and connection metrics without publishing heartbeats as business events.
6. Ignore unsupported message types safely while emitting a compatibility metric and sampled diagnostic metadata.

## Target Silver mapping

The following mapping is applied by Glue/Spark after Bronze, not by the source adapter before Kinesis.

| Silver field | Coinbase source or rule |
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

- Kinesis ordering is scoped to the selected raw-message partition strategy.
- Producer retries can create duplicate source messages; Silver deduplicates exploded trades using the deterministic trade identity.
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
