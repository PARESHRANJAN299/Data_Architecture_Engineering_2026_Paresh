# LCA Governed Source-to-Gold Streaming & AI Data Platform

![Project Status](https://img.shields.io/badge/Project_Status-In_Progress-F59E0B?style=for-the-badge)

**Project status:** 🟠 IN PROGRESS — Phase 1 Source to Stream

**Owner and Lead Architect:** Paresh Ranjan Rout

**Portfolio:** Data Architecture & Engineering 2026

**Current delivery stage:** Architecture baseline and Phase 1 — Source to Stream

## Mission

Build a reusable AWS data backbone that transports source events reliably, preserves immutable source history in Bronze, standardizes governed datasets in Silver, and produces trusted data for analytics and AI.

The Phase 1 source is locked to the **Coinbase Advanced Trade public WebSocket**. The adapter consumes `market_trades` and `heartbeats` for `BTC-USD` and `ETH-USD`. Coinbase is the proving source for a platform that can later support customer events, application telemetry, IoT feeds, transactions, and partner APIs.

## Locked Phase 1 source

| Property | Decision |
|---|---|
| Provider | Coinbase Advanced Trade |
| Endpoint | `wss://advanced-trade-ws.coinbase.com` |
| Business channel | `market_trades` |
| Operational channel | `heartbeats` |
| Initial products | `BTC-USD`, `ETH-USD` |
| Kinesis ordering domain | `event_source + product_id` |
| Silver trade identity | `coinbase.market_trade.{product_id}.{trade_id}` |
| Authentication | Public channels; no credential required for the initial scope |
| Source replay | Best-effort REST recovery plus Kinesis retention; no unsupported replay guarantee |

Detailed source behavior and mapping are defined in [`phase-1-source-to-stream/coinbase-source-specification.md`](phase-1-source-to-stream/coinbase-source-specification.md). The decision is recorded in [`ADR-004`](docs/decisions/ADR-004-coinbase-phase-1-source.md).

## Problem statement

Companies often integrate every new source with a separate pipeline. The result is duplicated engineering, inconsistent schemas, fragile retry logic, weak lineage, delayed analytics, and uncontrolled data entering AI systems.

This architecture establishes a repeatable source-to-consumption framework:

```mermaid
flowchart LR
    S[External and internal sources] --> A[Source adapters]
    A --> R[Raw source records]
    R --> K[Amazon Kinesis Data Streams]
    K --> B[S3 Bronze raw history]
    B --> V[Standardized Silver contracts]
    V --> G[Gold data products]
    G --> Q[Analytics, APIs, ML and AI]
```

## Target architecture

```mermaid
flowchart LR
    SRC[Coinbase Advanced Trade<br/>market_trades + heartbeats] --> ECS[ECS Fargate source adapter]
    ECS -->|raw Coinbase JSON| KDS[Kinesis Data Streams]
    ECS -->|delivery exhausted| DLQ[SQS dead-letter queue]
    ECS -. checkpoints and idempotency .-> DDB[DynamoDB control state]

    KDS --> FH[Amazon Data Firehose]
    FH --> BR[S3 Bronze<br/>immutable source JSON.GZIP]
    BR --> ETL[Glue / Spark / Flink]
    ETL -->|valid standardized rows| SI[Silver Iceberg tables]
    ETL -->|quality rejected| QUAR[S3 quality quarantine]
    SI --> TR[dbt / Glue transforms]
    TR --> GO[Gold data products]
    GO --> ATH[Athena]
    GO --> RS[Redshift Serverless]
    GO --> AI[SageMaker / Bedrock]

    GOV[Governance: IAM · KMS · Lake Formation · Catalog · CloudTrail] -. controls .-> VAL
    GOV -. controls .-> BR
    GOV -. controls .-> SI
    GOV -. controls .-> GO
```

## Architecture visuals

| View | Diagram |
|---|---|
| Three-phase delivery model | [Open PNG](architecture/three-phase-delivery-model.png) |
| Phase 1 source-to-stream flow | [Open PNG](architecture/phase-1-source-to-stream.png) |
| Governance control plane | [Open PNG](architecture/governance-control-plane.png) |
| Automated delivery flow | [Open PNG](architecture/automated-delivery-flow.png) |
| Iceberg logical-table backend | [Open SVG](architecture/iceberg-logical-table-backend.svg) |
| Phase 1 complete source-to-Silver flow | [Open SVG](architecture/phase-1-source-to-silver-complete-flow.svg) |

### Iceberg logical-table backend

![How Iceberg creates one logical Silver table](architecture/iceberg-logical-table-backend.svg)

## Three delivery phases

| Phase | Status | Outcome | Primary technologies | Exit evidence |
|---|---|---|---|---|
| 1. Source to Stream | **🟠 IN PROGRESS** | Reliable transport of unchanged Coinbase messages | Coinbase Advanced Trade, ECS Fargate, Kinesis, SQS DLQ, DynamoDB control state, CloudWatch, Terraform | Reconnect, heartbeat, retry, gap reporting and zero unexplained loss in controlled tests |
| 2. Bronze to Silver | ⚪ PLANNED | Immutable raw history and trustworthy datasets | Amazon Data Firehose, S3, Glue, Spark/Flink, Apache Iceberg, Glue Data Quality | Count reconciliation, deterministic deduplication, late-data handling, reproducible reprocessing |
| 3. Silver to Gold | ⚪ PLANNED | Governed business value and safe AI consumption | dbt/Glue, Athena, Redshift Serverless, QuickSight, SageMaker, Bedrock, Lake Formation | Approved metrics, lineage, role-based access, query SLOs, evaluated AI outputs |

## Architecture principles

1. Start with the business failure, not the AWS service.
2. Prefer managed services until control or portability requirements justify operational complexity.
3. Design for at-least-once delivery and idempotent processing; do not claim end-to-end exactly-once.
4. Preserve immutable raw history before applying business transformations.
5. Treat schemas, ownership, classification, quality, lineage, and retention as part of the data product.
6. Apply governance, observability, security, and cost controls from Phase 1.
7. Promote only when measurable architecture gates pass.
8. Record every material decision and its revisit trigger in an ADR.

## Repository map

| Path | Purpose |
|---|---|
| [`docs/01-problem-statement.md`](docs/01-problem-statement.md) | Business context, stakeholders, scope, and measurable outcomes |
| [`docs/02-target-architecture.md`](docs/02-target-architecture.md) | Logical architecture, flows, boundaries, and failure behavior |
| [`docs/03-technology-decisions.md`](docs/03-technology-decisions.md) | AWS service selection, alternatives, pros, cons, and triggers |
| [`docs/04-non-functional-requirements.md`](docs/04-non-functional-requirements.md) | Proposed reliability, performance, security, recovery, and cost SLOs |
| [`docs/05-delivery-roadmap.md`](docs/05-delivery-roadmap.md) | Three phases, work increments, gates, and evidence |
| [`docs/06-phase-1-source-to-silver-explainer.md`](docs/06-phase-1-source-to-silver-explainer.md) | Complete source-to-Silver backend, resolved questions and deployment proof |
| [`governance/`](governance/) | Governance operating model, control matrix, and approval gates |
| [`contracts/`](contracts/) | Raw transport rules, target Silver JSON Schema, sample event, and contract metadata |
| [`automation/`](automation/) | CI/CD, infrastructure, schema, security, and data-quality automation |
| [`architecture/`](architecture/) | Presentation-ready architecture, governance, and automation diagrams |
| [`phase-1-source-to-stream/`](phase-1-source-to-stream/) | **IN PROGRESS** — active Coinbase source-to-stream implementation |
| [`docs/presentation/`](docs/presentation/) | Executive and technical architecture deck |

## Current boundary

**🟠 Status: IN PROGRESS**

**🔒 Source locked:** Coinbase Advanced Trade public WebSocket using `market_trades` and `heartbeats` for `BTC-USD` and `ETH-USD`.

Phase 1 is the active build. Source selection, raw-transport architecture, governance baseline, source contract, and target Silver mapping are complete and repository-validated. Live Coinbase connectivity, adapter runtime, AWS infrastructure, deployment, and operational evidence have not yet passed their tests. Phases 2 and 3 remain target-state roadmaps until the Phase 1 gate passes.

## Phase 1 execution tracker

### Status legend

- ✅ **ACHIEVED & VERIFIED** — deliverable exists and its listed repository check passed.
- 🟠 **NEXT / IN PROGRESS** — current implementation focus; acceptance test has not passed yet.
- ⬜ **NOT STARTED** — no completion claim and no test evidence yet.

| Step | Deliverable | Status | Test or evidence |
|---:|---|---|---|
| 1 | Problem statement, scope and proposed outcomes | ✅ ACHIEVED & VERIFIED | Architecture documents and internal links validated |
| 2 | Coinbase source decision | ✅ ACHIEVED & VERIFIED — **LOCKED** | ADR-004 accepted; endpoint, channels and products documented from official sources |
| 3 | Target architecture, governance controls and AWS service decisions | ✅ ACHIEVED & VERIFIED | ADR set, control matrix, diagrams and presentation structural checks passed |
| 4 | Raw Coinbase transport contract and target Silver mapping | ✅ ACHIEVED & VERIFIED — design baseline | JSON/YAML parse checks passed; raw-payload and live-fixture validation remain Step 5 |
| 5 | Local Coinbase connectivity spike and captured fixtures | 🟠 **NEXT STEP** | Must prove subscribe, heartbeat, multi-trade parsing, reconnect and safe fixture capture |
| 6 | Containerized local source adapter | ⬜ NOT STARTED | Unit, contract and container smoke tests required |
| 7 | Kinesis producer and reconciliation consumer | ⬜ NOT STARTED | Local/AWS integration, partial-failure, duplicate and replay tests required |
| 8 | Terraform AWS foundation | ⬜ NOT STARTED | Format, validate, security scan, plan and clean-environment deployment required |
| 9 | ECS deployment, contracts, quarantine, DLQ and control state | ⬜ NOT STARTED | End-to-end source-to-Kinesis reconciliation and redrive tests required |
| 10 | Observability, security, recovery and cost evidence | ⬜ NOT STARTED | Alarms, failure injection, runbooks, access tests and unit-cost report required |
| 11 | Phase 1 Gate approval | ⬜ NOT STARTED | Every mandatory Gate 1 control must link to passing evidence |

### Immediate next steps

1. Create the local adapter and test directory structure.
2. Connect to Coinbase and subscribe to both locked channels.
3. Capture sanitized fixtures for heartbeat, single-trade and multi-trade messages.
4. Prove the Coinbase message is passed unchanged into the raw transport record; preserve `price` and `size` exactly as source strings.
5. Add reconnect, stale-heartbeat, duplicate, malformed-message and sequence-discontinuity tests.
6. Containerize and pass the local smoke test before creating AWS resources.

The detailed implementation order and definition of done are maintained in [`phase-1-source-to-stream/README.md`](phase-1-source-to-stream/README.md).

## Definition of portfolio quality

This project earns credibility through evidence rather than diagrams alone: reproducible infrastructure, failure-injection results, reconciliation reports, ADRs, cost estimates, security controls, runbooks, dashboards, and a traceable path from source event to business metric.

## Phase -1

### Complete entry flow: Coinbase source to Silver Iceberg

![Phase 1 source-to-Silver complete backend flow](architecture/phase-1-source-to-silver-complete-flow.svg)

The one-page view explains the complete backend behavior: Coinbase messages remain in source JSON through Kinesis and S3 Bronze; Firehose batches many records into immutable objects; Glue/Spark reads all new objects for the dataset and creates standardized Silver rows; Glue Catalog and Iceberg metadata allow Athena/Spark to resolve many physical Parquet files as one logical table.

This is the end-to-end learning and deployment view. The execution tracker above remains the authority for what has actually been built and verified.

The detailed questions, answers, service responsibilities, deployment order, tests and Silver business-approval loop are documented in [`docs/06-phase-1-source-to-silver-explainer.md`](docs/06-phase-1-source-to-silver-explainer.md).

### S3 prefix without manifests vs Iceberg with manifests

**Question asked:** If the Glue Catalog already contains an S3 location, why does an Iceberg table also require a manifest list?

| Ordinary external Parquet table — without Iceberg manifests | Iceberg table — with manifests |
|---|---|
| Glue Catalog points to an S3 prefix. | Glue Catalog points to the Iceberg table and its current metadata location. |
| The query engine discovers files from the prefix and partition information. | Iceberg metadata selects the current snapshot. |
| The prefix alone cannot identify current, replaced, deleted, old-snapshot or failed-write files. | The manifest list selects the snapshot's manifests; those manifests identify the exact active Parquet files. |
| No native Iceberg snapshot/time-travel view exists. | Atomic snapshots, file pruning and time travel are supported. |

> **S3 prefix says where files are stored. Iceberg manifests say which files are officially part of the table right now.**

```text
Athena/Spark query
    → Glue Catalog: locate the Iceberg table metadata
    → Iceberg metadata: select the current snapshot
    → manifest list: select the manifests for that snapshot
    → manifests: select the exact active Parquet files
    → Parquet files: read the actual rows
```

### What is an Iceberg snapshot?

**Question asked:** Does the Iceberg manifest capture the snapshot?

A snapshot is an immutable, committed version of the logical table at a particular moment. It does not contain the data rows and does not copy the Parquet files. It records the table operation, timestamp, parent snapshot and the location of its manifest list.

```text
Snapshot 003 — the committed table version
    → manifest-list-003.avro — manifests used by this version
    → manifest-001.avro and manifest-002.avro — file indexes
    → part-001.parquet, part-002.parquet, part-003.parquet — actual rows
```

The precise relationship is:

> **The snapshot is the table version. It points to a manifest list, and the manifests describe the exact physical-file state represented by that snapshot.**

When an append, update, delete, merge or compaction succeeds, Iceberg commits a new snapshot atomically. A failed operation does not replace the current snapshot, so readers never see a half-completed table version. Older snapshots also enable time travel and rollback until they are expired by the retention policy.

### Does the same Silver table continue growing every day?

**Question asked:** As Coinbase continuously generates streaming data and new objects move into S3, will the same Silver table increase in volume and will its maximum date advance every day?

Yes—after each successful incremental processing cycle, the same logical table contains more committed rows:

```text
Coinbase events
    → Kinesis records
    → Firehose-buffered Bronze objects
    → incremental Glue/Spark processing
    → new Silver Parquet files
    → new Iceberg snapshot and updated manifests
    → the same logical table contains more rows
```

```text
Snapshot 001 → data through 2026-08-11
Snapshot 002 → data through 2026-08-12
Snapshot 003 → data through 2026-08-13 — current
```

The table name remains `silver.fact_market_trade`. Athena normally reads its current committed snapshot, so `MAX(event_date)` advances when a newer event date has been successfully processed and committed.

```sql
SELECT
    MAX(source_event_time) AS latest_source_event,
    MAX(ingestion_time) AS latest_ingested_event
FROM silver.fact_market_trade;
```

The two timestamps distinguish when Coinbase generated the newest trade from when the platform received it. New data is visible in Silver only after Firehose flushes Bronze, Glue/Spark processes the new objects and Iceberg successfully commits the next snapshot.
