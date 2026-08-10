# ADR-002 — Use Amazon Kinesis Data Streams as the Backbone

- **Status:** Accepted for Phase 1
- **Owner:** Paresh Ranjan Rout
- **Decision date:** 2026-08-10

## Context

Multiple consumers require ordered event groups, independent progress, retention, replay, managed scaling, encryption, and AWS-native integration.

## Decision

Use Kinesis Data Streams in on-demand mode initially. Partition by the smallest business entity requiring order, such as `source + instrument`.

## Alternatives

- Amazon MSK: strong Kafka ecosystem but greater initial operational and cost complexity.
- SQS: excellent worker queue but not the primary replayable multi-consumer log.
- EventBridge: strong control-event routing but not the high-volume ordered backbone.

## Consequences

- Positive: managed stream, replay window, partition ordering, independent consumers.
- Negative: AWS-specific producer/consumer APIs, hot-partition risk, retention and enhanced-consumer cost.

## Revisit when

Kafka compatibility, connector demand, sustained throughput, retention, or unit cost invalidates the choice.
