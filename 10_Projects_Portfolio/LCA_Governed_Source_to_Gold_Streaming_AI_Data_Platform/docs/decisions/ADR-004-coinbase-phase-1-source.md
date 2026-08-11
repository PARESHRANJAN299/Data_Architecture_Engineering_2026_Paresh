# ADR-004 — Lock Coinbase Advanced Trade as the Phase 1 Source

- **Status:** Accepted
- **Date:** 2026-08-10
- **Owner:** Paresh Ranjan Rout

## Context

Phase 1 needs a free, genuine real-time source that exercises persistent connectivity, burst traffic, identity, ordering, duplicates, schema handling, recovery limits, and operational monitoring. The source must be strong enough to prove the platform without making source-specific complexity the entire project.

## Decision

Use the Coinbase Advanced Trade public WebSocket endpoint `wss://advanced-trade-ws.coinbase.com`.

- Consume `market_trades` as the business channel.
- Consume `heartbeats` as the connection-health channel.
- Start with `BTC-USD` and `ETH-USD`.
- Preserve one complete Coinbase `market_trades` source message per Kinesis record through Bronze.
- Apply trade explosion, deterministic identity and standardization when creating Silver.
- Defer the stateful `level2` order book until the market-trade path passes Gate 1.
- Use public REST market-trade data only for best-effort gap recovery; do not claim guaranteed source replay.

## Consequences

### Positive

- Genuine WebSocket lifecycle and burst behavior exercise the Fargate design.
- Stable trade and product identifiers support deterministic identity and reconciliation.
- Heartbeats support an explicit connection-health SLI.
- Two products prove partitioning without premature scale.
- Public market-data channels avoid credential handling in the initial source scope.

### Negative

- Source-side historical replay is limited, so some gaps may remain explicitly unrecoverable.
- Provider schema or policy changes require an owned compatibility response.
- Market data can be bursty and may create hot partitions if the product allowlist expands carelessly.

## Revisit triggers

- Coinbase changes public access, terms, rate limits, endpoint, or required authentication.
- Required recovery cannot be satisfied by Kinesis retention, captured Bronze history, or available REST data.
- The second adapter exposes an abstraction that the Coinbase-specific interface cannot support.
- Gate 1 passes and the portfolio is ready for the `level2` stateful-stream challenge.
