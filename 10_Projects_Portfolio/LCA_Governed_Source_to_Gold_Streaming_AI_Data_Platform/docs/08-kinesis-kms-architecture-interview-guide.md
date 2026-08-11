# Kinesis and KMS Architecture Interview Guide

**Owner:** Paresh Ranjan Rout

**Scope completed:** Kinesis stream configuration and AWS-managed KMS encryption

**Practice standard:** Every completed service is studied in three modes—Beginner, Medium and Company-scale Scenario.

> Company names below indicate interview-style scale and business context. They do not claim that any named company uses this exact architecture.

![Kinesis configuration and interview readiness](../architecture/kinesis-configuration-interview-readiness.svg)

## A reusable architecture-answer framework

For every scenario, answer in this order:

1. Clarify the business event and latency expectation.
2. Estimate records/second, bytes/second, burst pattern and retention.
3. Define the partition key and ordering boundary.
4. Explain delivery semantics, retries, duplicates and replay.
5. Add encryption, IAM, monitoring and sensitive-data controls.
6. Explain scaling, failure recovery and cost trade-offs.
7. State the tests and evidence required before declaring completion.

## Mode 1 — Beginner

### 1. What problem does Amazon Kinesis Data Streams solve?

**Strong answer:** It is a managed real-time transport that accepts records from producers, distributes them across shards, preserves order within a shard and temporarily retains records so one or more consumers can process or replay them.

### 2. Does Kinesis connect directly to Coinbase?

**Strong answer:** No. Coinbase generates WebSocket messages. Our ECS adapter will receive those messages and call Kinesis. Kinesis only receives records written by an authorized producer.

### 3. What is a shard?

**Strong answer:** A shard is the base capacity and ordering unit of a Kinesis stream. Records sharing a partition key map to a shard, and their sequence is maintained within that shard.

### 4. With one shard, are 1 MiB/second and 1,000 records/second alternatives?

**Strong answer:** No. Both ceilings must be respected. Tiny records can exceed the record-count ceiling; fewer large records can exceed the byte ceiling. Exceeding either can throttle writes.

### 5. What does one-day retention mean?

**Strong answer:** Every record remains accessible for a rolling 24 hours from its arrival. After it expires from Kinesis, a separate copy already delivered to S3 can remain available under the S3 lifecycle policy.

### 6. What is AWS-managed KMS key `aws/kinesis`?

**Strong answer:** It is an encryption key created and managed by AWS for Kinesis in our account. Kinesis uses it to encrypt records at rest and transparently decrypt them for authorized access. The application never stores the key material.

### 7. What is the difference between Kinesis and Firehose?

**Strong answer:** Kinesis is the real-time stream and replay buffer. Firehose is a managed delivery consumer that reads records, buffers them by time or size and writes batches to destinations such as S3.

## Mode 2 — Medium

### 1. How would you choose a partition key for Coinbase trades?

**Strong answer:** Start from the ordering requirement. A stable key such as `source + product_id` keeps trades for one product ordered, but capacity tests must prove that a popular product will not create a hot shard. Higher-cardinality keys improve distribution but reduce the ordering scope.

### 2. When would you change provisioned capacity to on-demand?

**Strong answer:** Use on-demand when traffic is difficult to predict or operational simplicity is more valuable than explicit capacity planning. Retain provisioned mode when throughput is measurable, shard-level ordering/control matters and predictable cost is desired. Compare real traffic and cost before switching.

### 3. Why should an architect avoid claiming exactly-once delivery?

**Strong answer:** Producer retries and consumer restarts can create duplicate delivery. Design for at-least-once transport, attach a deterministic event identity and make downstream processing idempotent. Exactly-once business outcomes require proof across the complete system, not a service-level slogan.

### 4. What is a hot shard and how do you address it?

**Strong answer:** A hot shard receives disproportionate traffic because of skewed partition keys. Detect throttling and per-shard imbalance, then redesign the key, add shards or introduce controlled key spreading while preserving the required ordering boundary.

### 5. AWS-managed key or customer-managed KMS key?

**Strong answer:** The AWS-managed key is suitable when simple encryption at rest is sufficient. Choose a customer-managed key when the organization requires custom key policy, controlled disablement, cross-account use, separation of duties or stronger audit/governance control. The additional control adds administration and failure modes.

### 6. Which metrics prove that the stream is healthy?

**Strong answer:** Track incoming records/bytes, write throttling, consumer read throttling, iterator age and application-level accepted/retried/failed counts. Enhanced shard metrics are useful when diagnosing imbalance, but they should be enabled intentionally because they add monitoring cost.

### 7. How do retention and replay influence recovery design?

**Strong answer:** The worst expected consumer outage must fit within Kinesis retention or another durable recovery source must exist. For outages beyond 24 hours, this project will replay immutable Bronze data from S3 rather than assume Kinesis still contains the records.

## Mode 3 — Company-scale scenarios

### 1. AWS-style multi-tenant service

**Question:** Thousands of customers publish events. One tenant can suddenly generate 40% of traffic. How would you prevent that tenant from harming everyone?

**Strong answer direction:** Establish tenant quotas, choose a partition strategy that avoids a single-tenant hot shard, monitor throttling by tenant and shard, isolate very large tenants when necessary, and define backpressure/DLQ behavior. Encryption and IAM must enforce tenant boundaries outside the partition key itself.

### 2. Netflix-like playback telemetry

**Question:** A new show release causes a sudden global traffic spike. Would one provisioned shard remain acceptable?

**Strong answer direction:** No conclusion is possible without load math. Calculate peak events and bytes per second, account for regional bursts, choose on-demand or pre-scale provisioned shards, distribute by a high-cardinality viewer/session key and load-test above the expected peak. Content ID alone could create a hot shard.

### 3. LinkedIn-like activity stream

**Question:** The business requires per-member activity ordering but not global ordering. What partition key would you propose?

**Strong answer direction:** Use member identity as the initial ordering boundary, assess celebrity/skew risk, and document that ordering is guaranteed only within the mapped shard sequence. If a member can be extremely hot, design controlled sub-partitioning with an explicit downstream reorder strategy.

### 4. Databricks-like lakehouse telemetry

**Question:** Streaming operational events must later become auditable lakehouse tables. Where does Kinesis stop and the lakehouse begin?

**Strong answer direction:** Kinesis provides temporary transport and replay. Firehose/S3 Bronze provides durable immutable raw history. Spark/Glue standardizes data and commits governed Iceberg Silver tables. Keep source JSON unchanged until Bronze, reconcile counts at each boundary and never treat Kinesis retention as the permanent archive.

### 5. Walmart-like retail events

**Question:** Holiday traffic increases store and online-order events by ten times. How do you design capacity and ordering?

**Strong answer direction:** Separate business ordering needs—such as per order or store—from global traffic. Model peak bytes and records, distribute using order/store identifiers, pre-scale or use on-demand, test throttling and use idempotent event identities so retries do not double-count sales.

### 6. FAANG-scale regional resilience

**Question:** A single AWS Region becomes unavailable. Is one Kinesis stream in `us-east-1` enough?

**Strong answer direction:** No. Define the RTO/RPO first. A regional architecture needs independent ingestion in another Region, regional producers and controlled aggregation or replication. Address duplicate identities, ordering changes, DNS/failover, KMS keys per Region and recovery testing. Do not claim global order.

### 7. Compliance-driven encryption change

**Question:** Security requires the ability to revoke stream access independently, inspect key usage and support cross-account consumers. Is `aws/kinesis` still sufficient?

**Strong answer direction:** Re-evaluate a customer-managed KMS key with explicit key policy, separation of duties, cross-account grants, rotation and break-glass recovery. Test producer and consumer permissions before migration because a key-policy mistake can stop the data plane.

### 8. Consumer outage longer than retention

**Question:** The consumer is down for 30 hours but retention is 24 hours. How is data recovered?

**Strong answer direction:** Kinesis alone cannot guarantee recovery of expired records. Restore from the durable Bronze copy in S3, process idempotently using event identity and reconcile recovered counts. If no durable copy exists, record a data-loss incident and reconsider retention/RPO before production.

## Interview completion checklist

- Can explain Kinesis, shard, partition key, retention and KMS without jargon.
- Can calculate both record-rate and byte-rate capacity.
- Can define the exact ordering boundary.
- Can explain at-least-once delivery, retries, duplicates and idempotency.
- Can choose AWS-managed versus customer-managed KMS using requirements.
- Can propose monitoring and failure evidence.
- Can distinguish a configured resource from a tested end-to-end pipeline.

## AWS references

- [Kinesis terminology and concepts](https://docs.aws.amazon.com/streams/latest/dev/key-concepts.html)
- [Kinesis quotas and limits](https://docs.aws.amazon.com/streams/latest/dev/service-sizes-and-limits.html)
- [Kinesis server-side encryption](https://docs.aws.amazon.com/streams/latest/dev/what-is-sse.html)
- [Kinesis CloudWatch monitoring](https://docs.aws.amazon.com/streams/latest/dev/monitoring-with-cloudwatch.html)
