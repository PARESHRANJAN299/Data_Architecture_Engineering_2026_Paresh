# 5. Reliability, Retention, Replay, and DLQ

## Broker and cluster
A broker is one Kafka server. A cluster is a group of brokers.

## Replication
```text
partition 0
├── leader on broker 1
├── replica on broker 2
└── replica on broker 3
```
The leader handles reads and writes. Replicas provide backup.

## Retention
Kafka keeps events based on time or size. Reading an event does not delete it.

## Replay
Consumers can reset offsets and read older events again to rebuild tables, recover from failure, or backfill data.

## Delivery semantics
- At-most-once: possible loss, no duplicate processing.
- At-least-once: no normal loss, but duplicates may occur.
- Exactly-once: final effect happens once with careful transactional design.

## DLQ
`commerce-events-dlq` stores invalid JSON, missing fields, unsupported schemas, or failed business rules.
