# Scala Streaming Producer

Planned responsibilities:

- call or subscribe to the selected open-source API
- generate deterministic event IDs
- publish Avro or Protobuf records to the event backbone
- apply partition-key strategy and schema versioning
- handle rate limits, retries, circuit breaking, and dead-letter records
- expose metrics for throughput, latency, failures, and throttling

The concrete API and event schema will be selected before implementation.
