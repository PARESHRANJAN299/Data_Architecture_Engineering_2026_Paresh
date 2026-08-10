# ADR-003 — Separate Retry Queues from Control State

- **Status:** Accepted for Phase 1
- **Owner:** Paresh Ranjan Rout
- **Decision date:** 2026-08-10

## Context

The earlier design placed all events in DynamoDB and used a poller to publish them to Kinesis. This provides explicit status but duplicates queue behavior and introduces polling, ordering, cleanup, and write-amplification complexity.

## Decision

- Publish directly from the adapter to Kinesis with bounded retries.
- Move exhausted delivery to SQS DLQ for investigation and controlled redrive.
- Store invalid contracts in S3 quarantine.
- Use DynamoDB only for checkpoints, idempotency keys, source configuration, and explicit control state.

## Consequences

- Positive: fewer writes and moving parts; each service matches its access pattern.
- Negative: accepted-event reconciliation spans producer, Kinesis, DLQ, and quarantine metrics.

## Revisit when

The source requires acknowledgement before Kinesis acceptance, very long store-and-forward behavior, or queryable per-event workflow state.
