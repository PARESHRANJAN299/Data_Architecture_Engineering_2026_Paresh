# High-Level Databricks Production Architecture

## 1. Scope

This project is intentionally Databricks-first. It demonstrates how one governed lakehouse supports streaming data engineering, BI, AI engineering, and deep-learning research while keeping the AWS-native portfolio as a separate implementation.

## 2. Logical architecture

### Source and producer layer

An open-source API continuously generates events. A Scala streaming producer converts source responses into a versioned event contract. The producer applies validation, serialization, compression, partition-key selection, retries with exponential backoff, rate-limit handling, and dead-letter routing.

### Event backbone

A Kafka-compatible event backbone decouples producers from Databricks. Topics are partitioned by a stable key such as `tenant_id`, `conversation_id`, or a hash that avoids hot partitions. Separate topics are used for raw events, retryable failures, and non-retryable dead-letter records.

The backbone absorbs traffic bursts and allows independent consumers to replay from committed offsets.

### Databricks ingestion

Use Lakeflow Spark Declarative Pipelines for new managed streaming pipelines where its constraints fit. Use custom Structured Streaming jobs when specialized stateful processing, custom connectors, or lower-level control is required.

Streaming checkpoints and schema metadata are stored in Unity Catalog-managed external locations. Jobs are configured for automatic restart and downstream writes are idempotent.

### Bronze layer

Bronze is append-only and preserves the original event payload plus ingestion metadata:

- source timestamp
- ingestion timestamp
- topic, partition, and offset
- schema version
- producer version
- correlation and trace identifiers
- raw payload
- rescue or parsing fields

Bronze is the replay and forensic source. It receives minimal transformations.

### Silver layer

Silver creates trusted, conformed datasets:

- schema enforcement and evolution rules
- deduplication using business keys and event identity
- late-event handling and watermarks
- normalization and reference-data enrichment
- PII classification, masking, tokenization, or deletion
- CDC application and current-state tables
- sessionization and conversation reconstruction
- quality expectations and quarantine tables

Stateful workloads use bounded state and carefully chosen watermarks. RocksDB state storage is evaluated for large state stores.

### Gold layer

Gold publishes domain-owned data products rather than one universal table:

- product and business KPIs
- model quality and latency metrics
- cost and token-usage metrics
- user and conversation aggregates
- feature-ready datasets
- training snapshots
- semantic models for BI

Complex analytical outputs can use incrementally refreshed materialized views; high-volume append flows use streaming tables.

### Serving and consumption

- **BI and Insights**: Databricks SQL serverless warehouses, semantic models, dashboards, alerts, and governed extracts.
- **AI Engineering**: feature tables, online/offline features, embedding pipelines, vector indexes, MLflow experiments, registered models, batch inference, and Model Serving.
- **Deep Learning / R&D**: reproducible training snapshots, distributed training compute, experiment tracking, notebooks, model evaluation, and governed access to sensitive corpora.
- **Data Engineering**: pipeline operations, contracts, lineage, quality, replay, optimization, and platform SLAs.

### Governance and security

Unity Catalog is the system of governance for tables, files, models, functions, volumes, lineage, and permissions. Catalog boundaries separate environments and, where necessary, regulated business domains.

Controls include:

- least-privilege service principals
- group-based grants
- row filters and column masks
- external locations and storage credentials
- secrets management
- audit logs and lineage
- cluster and compute policies
- private networking and egress restrictions

## 3. Extreme-scale design decisions

### Do not promise scale from record count alone

A trillion 200-byte events and a trillion 20-KB events are different systems. Capacity planning must include bytes per second, events per second, partition skew, state size, required latency, retention, number of consumers, and query concurrency.

### Partition for throughput and isolation

- provision enough event-bus partitions for target peak throughput
- avoid low-cardinality and skewed partition keys
- isolate high-volume domains into separate topics and pipelines
- compact small files before they create metadata bottlenecks
- use liquid clustering or appropriate table layout based on query patterns

### Control state growth

- define event-time watermarks
- expire inactive session state
- separate stateless and stateful transformations
- avoid unbounded stream-stream joins
- monitor state-store rows, bytes, commit time, and spill

### Design for replay

- persist immutable Bronze history
- track offsets and checkpoint ownership
- make MERGE and `foreachBatch` operations idempotent
- version schemas and transformations
- support bounded backfills on isolated job clusters

### Isolate workloads

Continuous streaming should not compete with BI queries or large training jobs. Use separate job clusters or serverless capabilities, independent quotas, and workload-specific policies.

## 4. Reliability targets to define

The project must set measurable SLOs rather than using only "highly available":

| Capability | Example production target to validate |
|---|---|
| Ingestion freshness | p95 source-to-Bronze under agreed latency |
| Trusted data freshness | p95 source-to-Silver/Gold under agreed latency |
| Data completeness | expected versus received event counts |
| Duplicate rate | below domain threshold after Silver |
| Pipeline availability | monthly successful processing objective |
| Recovery | RTO and RPO per data product |
| BI performance | dashboard p95 query time and concurrency |
| Model serving | p95 latency, error rate, and availability |

The values are intentionally left for load testing and stakeholder agreement.
