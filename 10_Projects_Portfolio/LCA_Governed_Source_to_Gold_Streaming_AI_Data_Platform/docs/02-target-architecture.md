# Target Architecture and Data Flow

## Architectural intent

Separate the platform into a **data plane**, which transports and transforms events, and a **control plane**, which manages contracts, configuration, identity, deployments, evidence, and policy.

## System context

```mermaid
flowchart TB
    P[Data producers] --> LCA[LCA governed streaming platform]
    LCA --> A[Analysts and BI]
    LCA --> AP[Operational applications and APIs]
    LCA --> M[ML and AI teams]
    SEC[Security, governance and FinOps] --> LCA
    ENG[Platform and data engineering] --> LCA
```

## End-to-end logical flow

```mermaid
flowchart LR
    subgraph P1[Phase 1 — Source to Stream]
      S[Coinbase Advanced Trade<br/>market_trades + heartbeats] --> F[ECS Fargate adapter]
      F --> C[Canonical contract]
      C --> K[Kinesis Data Streams]
      C -->|invalid| Q[S3 quarantine]
      F -->|retry exhausted| D[SQS DLQ]
      F -.-> M[DynamoDB control state]
    end

    subgraph P2[Phase 2 — Bronze to Silver]
      K --> H[Amazon Data Firehose]
      H --> B[S3 Bronze]
      B --> X[Glue / Spark / Flink]
      X --> I[Silver Iceberg]
    end

    subgraph P3[Phase 3 — Silver to Gold]
      I --> T[dbt / Glue]
      T --> G[Gold products]
      G --> AN[Athena / Redshift / QuickSight]
      G --> AI[SageMaker / Bedrock]
    end
```

## Phase 1 detailed behavior

1. An ECS Fargate service connects to `wss://advanced-trade-ws.coinbase.com` and subscribes to `market_trades` and `heartbeats` for `BTC-USD` and `ETH-USD`.
2. Heartbeats update connection-health metrics and are not published as market-trade business events.
3. A Coinbase message can contain multiple trades; the adapter emits one canonical event per trade without discarding the relevant source fields.
4. It creates `event_id = coinbase.market_trade.{product_id}.{trade_id}`, timestamps receipt, and uses `coinbase.advanced_trade#{product_id}` as the partition key.
5. AWS Glue Schema Registry enforces the registered contract and compatibility policy.
6. Valid events are batch-written to Kinesis using bounded retries, exponential backoff, and partial-failure handling.
7. Invalid events are encrypted and quarantined in S3 with a non-sensitive rejection reason.
8. Events that exhaust delivery retries go to an SQS DLQ for investigation and redrive.
9. DynamoDB stores the last observed source sequence, connection state, and idempotency records where required.
10. CloudWatch exposes connection state, heartbeat age, sequence gaps, accepted/rejected records, delivery failures, throttling, lag, and cost-related utilization.

## Ordering and identity

- Ordering is required only within `coinbase.advanced_trade + product_id`; global ordering is not promised.
- The Kinesis partition key uses that ordering domain and is monitored for hot partitions.
- `event_id` is deterministically derived from Coinbase `product_id` and `trade_id`.
- All consumers are idempotent because producer retries and downstream delivery can create duplicates.
- `source_event_time`, `ingestion_time`, and `processing_time` remain separate.

## Failure paths

| Failure | Expected response | Evidence |
|---|---|---|
| Source disconnect | Backoff, reconnect, resume from source capability/checkpoint | Reconnection test and gap report |
| Invalid schema | Quarantine; never silently discard | Quarantine object and metric |
| Partial `PutRecords` failure | Retry only failed records | Structured log and retry metric |
| Kinesis throttling | Backoff, scale review, alarm | Throttle alarm and runbook execution |
| Retry exhaustion | SQS DLQ with safe diagnostic metadata | DLQ alarm and redrive test |
| Adapter crash | ECS service replaces unhealthy task | Recovery-time measurement |
| Duplicate event | Idempotent Silver processing | Deduplication reconciliation |
| Secret exposure attempt | CI secret scan blocks merge/deploy | Pipeline evidence |

## Data zones

| Zone | Purpose | Mutation policy | Typical access |
|---|---|---|---|
| Quarantine | Invalid or policy-rejected records | Append-only; controlled remediation | Data steward and platform role |
| Bronze | Immutable source truth | Append-only; lifecycle-managed | Restricted engineering role |
| Silver | Validated, standardized, deduplicated | Rebuildable from Bronze | Data engineers and approved analysts |
| Gold | Approved business metrics and features | Versioned data product | BI, applications, ML/AI consumers |

## Silver Iceberg logical-table backend

![Iceberg logical-table backend](../architecture/iceberg-logical-table-backend.svg)

For each approved Silver dataset, Glue/Spark reads all new objects from the matching Bronze prefix and commits standardized rows to one Iceberg table. For example, many Coinbase `market_trades` batch objects become the single logical table `silver.fact_market_trade`.

The table is resolved in this order:

```text
Athena / Spark
    → AWS Glue Data Catalog table entry
    → current Iceberg metadata JSON
    → snapshot and manifest files
    → physical Parquet data files in S3
```

The number of Bronze batch objects does not determine the number of Silver tables. Dataset ownership and schema determine the tables. An Iceberg table remains one logical dataset even though continuous appends create multiple physical Parquet files managed by its metadata and periodically optimized through compaction.

## Trust boundaries

- The public internet terminates at the source adapter's outbound connection; no public inbound listener is required for ingestion.
- Credentials come from Secrets Manager and task roles, never images or repository files.
- Private subnets use controlled egress and VPC endpoints where justified by cost and threat model.
- Separate roles exist for deployment, task execution, runtime producer, quarantine writer, observer, and break-glass operations.
- Encryption uses customer-managed KMS keys where control, audit, or separation requirements justify them.

## Target evolution

The Phase 1 single-account learning environment must preserve interfaces that can later move into separate development, staging, production, security, and data-governance accounts without redesigning event contracts.
