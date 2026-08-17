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
| First manually configured AWS service | [Open SVG](architecture/manual-kinesis-first-service.svg) |
| Kinesis 24-hour retention explained | [Open SVG](architecture/kinesis-24-hour-retention.svg) |
| Kinesis completion and interview readiness | [Open SVG](architecture/kinesis-configuration-interview-readiness.svg) |

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
| [`docs/07-phase-1-manual-aws-implementation.md`](docs/07-phase-1-manual-aws-implementation.md) | Manual Kinesis build, capacity theory, retention and verified AWS progress |
| [`docs/08-kinesis-kms-architecture-interview-guide.md`](docs/08-kinesis-kms-architecture-interview-guide.md) | Beginner, Medium and Company-scale Scenario interview preparation |
| [`docs/09-ecs-iam-architecture-interview-guide.md`](docs/09-ecs-iam-architecture-interview-guide.md) | ECS task/execution-role architecture and three-mode interview preparation |
| [`docs/10-ecs-ecr-fargate-simple-explainer.md`](docs/10-ecs-ecr-fargate-simple-explainer.md) | Beginner explanation of packaging, runtime, task replacement and data flow |
| [`docs/11-ecs-ecr-fargate-data-engineering-architecture-interview-guide.md`](docs/11-ecs-ecr-fargate-data-engineering-architecture-interview-guide.md) | Three-mode Data Engineer and Data Architect interview preparation |
| [`governance/`](governance/) | Governance operating model, control matrix, and approval gates |
| [`contracts/`](contracts/) | Raw transport rules, target Silver JSON Schema, sample event, and contract metadata |
| [`automation/`](automation/) | CI/CD, infrastructure, schema, security, and data-quality automation |
| [`architecture/`](architecture/) | Presentation-ready architecture, governance, and automation diagrams |
| [`phase-1-source-to-stream/`](phase-1-source-to-stream/) | **IN PROGRESS** — active Coinbase source-to-stream implementation |
| [`docs/presentation/`](docs/presentation/) | Executive and technical architecture deck |

## Current boundary

**🟠 Status: IN PROGRESS**

**🔒 Source locked:** Coinbase Advanced Trade public WebSocket using `market_trades` and `heartbeats` for `BTC-USD` and `ETH-USD`.

Phase 1 is the active build. Source selection, raw-transport architecture, governance baseline, source contract, target Silver mapping, live Coinbase connectivity and the containerized local adapter are complete and repository-validated. The encrypted Kinesis stream and initial ECS IAM configuration are complete; exact-stream allows and wildcard denies passed policy simulation. Runtime role assumption, producer delivery, Firehose/S3, ECS deployment and production-scale operational evidence have not yet passed their tests. Phases 2 and 3 remain target-state roadmaps until the Phase 1 gate passes.

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
| 5 | Local Coinbase connectivity spike and sanitized fixtures | ✅ **ACHIEVED & VERIFIED** | 20 live market messages containing 230 trades, 10 heartbeats, both products, 0 sequence gaps and 0 quarantine; summary/hash committed without payloads |
| 6 | Containerized local source adapter | ✅ **ACHIEVED & VERIFIED** | Initial 12 unit/contract tests passed; non-root UID `10001`; bounded live container smoke test passed |
| 7 | Kinesis producer and reconciliation consumer | 🟠 **IN PROGRESS** — local sink and stream smoke verified | Stream is Active/encrypted; 4 focused sink tests and all 16 adapter tests pass; manual write/read passed; application delivery, retry, duplicate and replay remain |
| 8 | Manual AWS foundation and later infrastructure-as-code reproduction | 🟠 **IN PROGRESS** | Kinesis and initial ECS IAM evidence committed; networking, ECR, ECS and reproducible automation remain |
| 9 | ECS deployment, contracts, quarantine, DLQ and control state | ⬜ NOT STARTED | End-to-end source-to-Kinesis reconciliation and redrive tests required |
| 10 | Observability, security, recovery and cost evidence | ⬜ NOT STARTED | Alarms, failure injection, runbooks, access tests and unit-cost report required |
| 11 | Phase 1 Gate approval | ⬜ NOT STARTED | Every mandatory Gate 1 control must link to passing evidence |

### Immediate next steps

1. Create the ECR repository and publish the versioned container image.
2. Create the ECS runtime and prove temporary role credentials, ECR pull and CloudWatch logging.
3. Prove the first live `PutRecord` reaches the exact Kinesis stream unchanged.
4. Add controlled retry, batching where justified and reconciliation metrics.
5. Add a reconciliation consumer and prove accepted, acknowledged, retried and failed counts balance.

The detailed implementation order and definition of done are maintained in [`phase-1-source-to-stream/README.md`](phase-1-source-to-stream/README.md).

## Phase 1 source-to-stream achievement

**Status: ✅ ACHIEVED & VERIFIED — 16 August 2026**

The live AWS runtime is now operating end to end:

```text
Coinbase WebSocket
    → phase1-v2 Python adapter
    → ECS service on AWS Fargate
    → IAM-authorized Kinesis PutRecord
    → lca-coinbase-market-trades-dev
```

Verified evidence includes one healthy ECS task, successful CloudWatch connection and subscription logs, continuous Kinesis `PutRecord` activity, successful-write ratio `1`, approximately `4 ms` write latency, and 48 live Coinbase `market_trades` records visible in Kinesis Data Viewer.

Detailed completion record: [docs/13-phase-1-source-to-stream-completion.md](docs/13-phase-1-source-to-stream-completion.md).

> Scope boundary: this completes the Source-to-Stream runtime. Firehose → S3 Bronze is the next milestone and is not yet marked complete.

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

## Phase 1 manual AWS implementation — IN PROGRESS

The first manually configured AWS service is complete for the current development scope: Amazon Kinesis Data Streams in `us-east-1`. This means its resource controls are configured; it does not yet mean Coinbase data delivery is complete.

![Phase 1 first manually configured AWS service](architecture/manual-kinesis-first-service.svg)

### What we learned

- Coinbase creates live messages; Kinesis receives records written by our future ECS adapter.
- Firehose will be a downstream Kinesis consumer. It will buffer many records and deliver Bronze objects to S3.
- One provisioned shard supports up to **1 MiB/second and 1,000 records/second** for writes. Both limits must be respected; exceeding either can throttle the producer.
- A one-day retention period means each Kinesis record remains readable for 24 hours from arrival. It does not define future S3 Bronze retention.
- Server-side encryption is enabled with the AWS-managed KMS key `aws/kinesis`; application code never stores the encryption key.

![Kinesis one-day retention explained](architecture/kinesis-24-hour-retention.svg)

### Manual AWS progress tracker

| Step | Deliverable | Status | Evidence or next test |
|---:|---|---|---|
| 1 | Create `lca-coinbase-market-trades-dev` | ✅ **ACHIEVED & VERIFIED** | Stream observed Active; [redacted evidence](phase-1-source-to-stream/evidence/manual-kinesis-stream-creation.json) |
| 2 | Enable server-side encryption | ✅ **ACHIEVED & VERIFIED** | Encryption update succeeded with AWS-managed `aws/kinesis` |
| 2A | Manually write and read one Kinesis record | ✅ **ACHIEVED & VERIFIED** | CloudShell write returned KMS; Data Viewer returned the expected record; [redacted evidence](phase-1-source-to-stream/evidence/manual-kinesis-write-read-smoke-test.json) |
| 3 | Create ECS task and execution roles | ✅ **ACHIEVED & VERIFIED** | Trust verified; exact-stream allow and wildcard-deny simulations passed; [redacted evidence](phase-1-source-to-stream/evidence/manual-ecs-iam-foundation.json) |
| 3A | Validate ECS, ECR, Fargate and IAM runtime responsibilities | ✅ **ACHIEVED & VERIFIED — DESIGN** | Final numbered blueprint and question-driven explanation completed |
| 4A | Implement and locally test `KinesisRawMessageSink` | ✅ **ACHIEVED & VERIFIED — LOCAL** | 4 focused tests and all 16 adapter tests passed; [evidence](phase-1-source-to-stream/evidence/local-kinesis-sink-test.json) |
| 4B | Publish a secure versioned image to ECR | ✅ **ACHIEVED & VERIFIED** | `phase1-v2` built, live-tested and pushed; ECR basic scan completed successfully with no reported findings |
| 4C | Deploy image to ECS/Fargate | 🟠 **NEXT** | Create the Task Definition, start a healthy task, verify runtime role assumption and inspect CloudWatch logs |
| 5 | Prove Coinbase → ECS → Kinesis | ⬜ **NOT STARTED** | Count reconciliation and unchanged-message evidence required |
| 6 | Add Firehose → S3 Bronze | ⬜ **NOT STARTED** | Buffered objects and source-to-Bronze reconciliation required |

Full configuration reasoning: [`docs/07-phase-1-manual-aws-implementation.md`](docs/07-phase-1-manual-aws-implementation.md).

> Security evidence rule: screenshots containing the AWS account ID or full ARN are not published. The repository stores redacted configuration evidence instead.

### Kinesis completion boundary and interview preparation

![Kinesis configuration completion and interview readiness](architecture/kinesis-configuration-interview-readiness.svg)

**Kinesis resource configuration is complete. Kinesis end-to-end delivery remains in progress.** The next proof must show that the ECS adapter can write unchanged Coinbase messages, recover from failures and reconcile every accepted record.

Architecture interview preparation now follows three permanent modes:

1. **Beginner** — explain the service, terminology and data flow clearly.
2. **Medium** — justify partitioning, capacity, replay, encryption, monitoring and cost trade-offs.
3. **Company-scale Scenario** — solve AWS-style SaaS, Netflix-like streaming, LinkedIn-like activity, Databricks-like lakehouse, Walmart-like retail and FAANG-scale resilience problems.

Practice guide: [`docs/08-kinesis-kms-architecture-interview-guide.md`](docs/08-kinesis-kms-architecture-interview-guide.md).

### ECS IAM foundation — ACHIEVED & VERIFIED

```text
Coinbase application
    → lca-coinbase-ecs-task-role-dev
    → PutRecord + PutRecords
    → exact development Kinesis stream only

ECS/Fargate platform
    → lca-coinbase-ecs-execution-role-dev
    → AmazonECSTaskExecutionRolePolicy
    → ECR image pull + CloudWatch log delivery
```

The task role's exact-stream positive test returned **Allowed** for both write actions. The wildcard-resource negative test returned **ImplicitDeny**, proving the role cannot write to every stream. Both roles trust `ecs-tasks.amazonaws.com`; no static AWS keys are stored in code, the container or GitHub.

Runtime behavior is intentionally still unverified: ECS has not yet assumed the roles, pulled an image, delivered logs or written a Coinbase record.

- Evidence: [`manual-ecs-iam-foundation.json`](phase-1-source-to-stream/evidence/manual-ecs-iam-foundation.json)
- Interview preparation: [`docs/09-ecs-iam-architecture-interview-guide.md`](docs/09-ecs-iam-architecture-interview-guide.md)

> Screenshot rule: account IDs and full role/stream ARNs remain excluded from committed evidence.

### Simple explanation: where Python runs

There are two different flows, and keeping them separate removes most of the confusion:

```text
APPLICATION DEPLOYMENT

Python code → container image → ECR → ECS → Fargate → Python is running
```

```text
BUSINESS DATA

Coinbase → running Python adapter → Kinesis → Firehose → S3 Bronze
```

The services have one simple responsibility each:

```text
Python adapter = worker that carries messages
ECR            = warehouse storing the packaged worker software
ECS            = manager maintaining the required number of tasks
Fargate        = managed computer where the worker runs
Kinesis        = streaming destination receiving the messages
```

With `desired count = 1`, an ECS Service attempts to keep one adapter task running. If that task stops, ECS asks Fargate for a replacement in the configured network. The new task pulls the image, starts Python, reconnects to Coinbase and resumes delivery. A short restart gap can still occur, so reconnect and reconciliation controls remain necessary.

Complete step-by-step explanation: [`docs/10-ecs-ecr-fargate-simple-explainer.md`](docs/10-ecs-ecr-fargate-simple-explainer.md).

### ECS, ECR and Fargate interview preparation

The completed learning is converted into separate **Data Engineer** and **Data Architect** expectations across three modes:

1. **Beginner** — image, container, ECR, ECS, Fargate, task definition, service and IAM roles.
2. **Medium** — image pull, logging, immutable deployment, scanning, lifecycle, runtime choice and availability trade-offs.
3. **Company-scale Scenario** — restart loops, duplicates, rollback, zero-downtime WebSocket deployment, environment isolation and cross-account image delivery.

Interview guide: [`docs/11-ecs-ecr-fargate-data-engineering-architecture-interview-guide.md`](docs/11-ecs-ecr-fargate-data-engineering-architecture-interview-guide.md).

## Phase 1 final runtime blueprint and question-driven explanation

![Phase 1 final runtime blueprint](architecture/phase-1-runtime-flow-numbered-blueprint.png)

Editable source: [`architecture/phase-1-runtime-flow-numbered-blueprint.svg`](architecture/phase-1-runtime-flow-numbered-blueprint.svg)

### How the Dockerfile becomes our running Python adapter

```text
1. Dockerfile contains the instructions
   ↓
2. Run docker build
   ↓
3. Docker follows each Dockerfile instruction
   ↓
4. Docker creates the image: phase1-v2
   ↓
5. Push the image to ECR
   ↓
6. Fargate pulls the image
   ↓
7. Fargate creates a container from the image
   ↓
8. The container automatically runs the CMD instruction
   ↓
9. Our Python adapter starts
```

The three objects must not be confused:

```text
Dockerfile = written build and startup instructions
Image      = completed, versioned application package
Container  = running instance created from the image
```

Docker does not place everything in the image automatically. During `docker build`, it reads the Dockerfile from top to bottom. `FROM` supplies the Linux and Python foundation, `RUN` installs required packages, `COPY` adds our source code, and `CMD` records the default command that a future container will execute. The image itself does not run; ECS/Fargate creates and runs a container from that image.

### Latest implementation checkpoint — phase1-v2

```text
Changed the base image to Python 3.11.15 on Alpine 3.23
    ↓
Built phase1-v2 in CloudShell (81.2 MB)
    ↓
Started a container from phase1-v2
    ↓
Connected and subscribed to the Coinbase WebSocket
    ↓
Received exactly 1 live market message
    ↓
Wrote exactly 1 JSONL record with 0 quarantine and sequence errors
    ↓
Tagged phase1-v2 with the private ECR repository address
    ↓
Pushed phase1-v2 to ECR successfully
    ↓
ECR basic security scan completed successfully
    ↓
No vulnerability findings were reported
```

Current decision: `phase1-v2` passed the configured ECR basic-scan gate and is approved for the Phase 1 ECS deployment step. An empty `SeverityCounts` result means that this scan reported no findings; it is evidence for this gate, not a claim that software can never contain risk.

> **Evidence boundary:** this diagram describes the intended Phase 1 runtime. The Kinesis stream, IAM roles, ECR repository, local container and individual permissions have been tested as recorded above. The complete ECS/Fargate runtime and end-to-end Coinbase-to-Kinesis delivery are not marked verified until their required deployment evidence passes.

### The architecture contains two different flows

Keeping deployment activity separate from business data movement removes most of the confusion.

**Deployment flow — how the application reaches AWS compute:**

```text
Python source code + libraries + Dockerfile
    → CloudShell builds a Docker image
    → docker push stores the image in Amazon ECR
    → ECS Task Definition references the ECR image URI
    → ECS uses the Execution Role to pull the image
    → Fargate starts a container from that image
    → the Python adapter starts inside the container
```

**Runtime flow — how each Coinbase message reaches Kinesis:**

```text
Coinbase WebSocket
    → live source JSON
    → Python adapter running in the Fargate container
    → Python calls Kinesis PutRecord or PutRecords
    → Amazon Kinesis Data Stream receives the record
```

ECR is involved when the application is deployed or a replacement task starts. ECR is **not** in the live Coinbase-to-Kinesis data path.

### Where does Amazon ECR exist?

Amazon ECR is a separate AWS-managed regional service. It is not located inside CloudShell, EC2, ECS or the Fargate task.

```text
AWS account
└── Region: us-east-1
    └── Amazon ECR
        └── Private repository: lca-coinbase-adapter-dev
            ├── image tag: phase1-v1
            └── image tag: phase1-v2, pushed and awaiting scan completion
```

AWS manages ECR's underlying physical servers and storage. The project manages repositories, image tags, encryption, scanning, lifecycle and access policies—not ECR's storage machines.

### What exactly does ECR store?

ECR is a warehouse specifically for **container images**. A container image is the packaged application required to start a consistent container:

- application source code;
- Python runtime;
- installed dependencies from `requirements.txt`;
- operating-system libraries supplied by the base image;
- filesystem content copied by the Dockerfile; and
- the configured startup command.

ECR can contain many repositories and many versioned image tags. For example, a company could store a Coinbase adapter image, customer API image and data-quality service image in separate repositories.

```text
Amazon ECR
├── lca-coinbase-adapter-dev
│   ├── phase1-v1
│   └── phase1-v2
├── customer-api
│   ├── v1.0
│   └── v2.0
└── data-quality-service
    └── v3.0
```

However, ECR does **not** store:

- an API endpoint or URL;
- Coinbase or customer business data;
- live API responses;
- Kinesis records; or
- general lakehouse files such as JSON, CSV or Parquet.

An API application's container image can be stored in ECR. The API endpoint itself is normally exposed through an Application Load Balancer, API Gateway or another networking service. Business data belongs in services such as S3, RDS or DynamoDB.

```text
ECR                 → stores the packaged API application image
ECS/Fargate         → runs the API application container
API Gateway or ALB  → provides the reachable API endpoint
S3/RDS/DynamoDB     → stores the application's business data
```

### Docker image versus running container

These are related but not identical:

```text
Dockerfile  = instructions for packaging the application
Docker image = immutable packaged application stored in ECR
Container    = running instance created from that image
```

The container is not literally stored “inside memory.” It runs as an isolated process on the Fargate task and consumes the CPU, memory, networking and temporary storage assigned to that task.

```text
Amazon ECR
    → permanent stored image

AWS Fargate task
    → allocated CPU + memory + networking + ephemeral storage
    → running container created from the ECR image
    → Python adapter process running inside the container
```

When the Fargate task stops, its running container and temporary local storage disappear. The original versioned image remains in ECR and can be pulled again.

### What do Fargate and ECS each do?

Fargate provides the managed computer capacity. ECS provides orchestration.

```text
Fargate = supplies CPU, memory, networking and temporary task storage
ECS     = defines, starts, monitors and replaces the required task
```

With ECS Service `desired count = 1`, ECS continually compares desired state with actual state:

```text
Desired: 1 running task
Actual:  1 running task  → no action

Desired: 1 running task
Actual:  0 running tasks → ECS requests a replacement Fargate task
```

A replacement task pulls the configured image from ECR, starts a new container and runs the Python startup command. Replacement improves availability but does not guarantee zero message loss during a WebSocket restart; reconnect, checkpoint and reconciliation controls are still required.

### Why are there two ECS IAM roles?

Both roles grant temporary permissions, but different actors use them.

#### ECS Task Role

The Python application uses the Task Role after the container starts.

```text
Python application
    → receives temporary Task Role credentials
    → calls kinesis:PutRecord or kinesis:PutRecords
    → writes only to the permitted Kinesis stream
```

The Task Role never carries, writes or transforms data. Python performs the API call; the role only determines whether AWS authorizes it.

#### ECS Execution Role

The ECS/Fargate platform uses the Execution Role to prepare and operate the task.

```text
ECS/Fargate platform
    → assumes Execution Role
    → receives temporary credentials
    ├── pulls image layers from Amazon ECR
    └── writes container logs to CloudWatch Logs
```

The Execution Role does not pull an image or send logs by itself. ECS performs those actions; the role only authorizes them. The Python application does not normally use the Execution Role.

### How do logs reach CloudWatch?

The container writes operational messages to standard output and standard error. The ECS `awslogs` log driver sends those streams to CloudWatch Logs using permissions supplied by the Execution Role.

```text
Python print/logging output
    → container stdout/stderr
    → ECS awslogs log driver
    → CloudWatch log group and log stream
```

CloudWatch should receive operational information such as:

- Coinbase connection and reconnection events;
- subscription success or failure;
- processed-message counts;
- malformed-message or quarantine errors;
- heartbeat age and sequence-gap diagnostics; and
- container startup, shutdown and exception details.

CloudWatch is not the destination for the Coinbase market dataset. Market records go to Kinesis; CloudWatch receives the application's operational logs and metrics.

### Complete startup sequence

1. CloudShell builds a versioned Docker image from the Dockerfile.
2. The image is pushed to the private ECR repository.
3. The ECS Task Definition references the exact image URI and identifies both IAM roles.
4. ECS Service sees that one task is required.
5. ECS/Fargate assumes the Execution Role and receives temporary credentials.
6. ECS pulls the image layers from ECR.
7. Fargate allocates CPU, memory, networking and ephemeral storage.
8. Fargate creates the container and runs the configured Python command.
9. The Python adapter receives temporary Task Role credentials.
10. Python connects to the Coinbase WebSocket and receives live JSON messages.
11. Python calls Kinesis `PutRecord` or `PutRecords`; the Task Role authorizes the call.
12. The ECS log driver forwards container logs to CloudWatch; the Execution Role authorizes the log writes.
13. If the task stops, ECS requests a replacement and repeats the relevant startup steps.

### Short memory model

```text
CloudShell     = build and test workshop
Dockerfile     = packaging instructions
Docker image   = packaged Python application
ECR            = permanent container-image warehouse
Task Definition = runtime blueprint
ECS Service    = manager keeping the desired task count running
Fargate        = managed computer running the container
Task Role      = permission for Python to call Kinesis
Execution Role = permission for ECS to pull ECR images and deliver logs
CloudWatch     = operational logs and monitoring
Kinesis        = live streaming-record destination
```
