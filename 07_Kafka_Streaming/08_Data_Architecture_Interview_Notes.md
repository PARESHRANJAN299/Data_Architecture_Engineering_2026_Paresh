# 8. Data Architecture Interview Notes

## Scalability
Kafka scales with more partitions, brokers, and consumers.

## Availability
Kafka uses replication and leader election. Stream processors use checkpoints and restart logic.

## Durability
Kafka writes events to disk. Delta Lake stores persistent table data.

## Idempotency
Processing the same event twice should not create an incorrect result. Use `event_id` for deduplication.

## Schema evolution
Add a `schema_version` field and handle compatible and breaking changes carefully.

## Backpressure
When producers are faster than consumers, Kafka buffers events and consumer lag increases.

## Data quality
Validate required fields, timestamps, quantities, amounts, currency, keys, and unique event IDs.

## Observability
Monitor producer errors, broker health, throughput, lag, latency, DLQ count, freshness, failures, and cost.

## Security
Use TLS, authentication, ACLs, private networking, secret management, and audit logs.

## Strong project answer
> Scala producers create product and commerce events and publish them to domain-specific Kafka topics using business keys. Kafka provides buffering, partitioning, replay, and decoupling. Databricks Structured Streaming writes raw events to Bronze Delta tables, Silver performs validation and deduplication, and Gold provides business-ready datasets for BI and machine learning.
