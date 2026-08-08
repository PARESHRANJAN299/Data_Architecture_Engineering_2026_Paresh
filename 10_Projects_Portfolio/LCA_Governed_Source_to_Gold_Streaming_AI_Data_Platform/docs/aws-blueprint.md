# Enterprise Data Architecture — AWS Blueprint

Your architecture vision, mapped to concrete AWS services. Review this before the deck is built.

---

## Capability → AWS service mapping

### Phase 1 — Source → Bronze

| Your capability | AWS service | Why this one |
|---|---|---|
| CDC for incremental loading | **AWS DMS** (CDC mode) | Purpose-built for ordered, transactional change capture from relational sources. Reads the DB transaction log rather than polling |
| Real-time streaming ingestion | **Kinesis Data Streams** | Replayable and multi-consumer — Silver processing and a real-time alerting consumer can read the same stream independently |
| Device / telemetry ingestion | **AWS IoT Core → Kinesis** | Devices speak MQTT, not the Kinesis SDK. IoT Core is the bridge |
| Automated ingestion & delivery | **Amazon Data Firehose** | Buffers, batches, converts to Parquet, delivers to S3 with no code |
| Source-to-Bronze schema management | **Glue Schema Registry** | Validates every event at write time. A producer sending a malformed payload is rejected at the door instead of corrupting Bronze |
| Column-level masking (salary, PII) | **Firehose → Lambda transformation** | Masking applied *before* the record lands. Bronze never physically holds the raw sensitive value |
| PII / confidential governance | **Amazon Macie** + **Lake Formation** | Macie discovers PII you did not know about; Lake Formation enforces who can see it |
| Encryption | **KMS** + **VPC endpoints** | At rest and in transit, no public network path |
| Lineage & metadata | **Glue Data Catalog** + **SageMaker Catalog** | Column-level lineage captured automatically |
| Auditability | **CloudTrail** + **CloudWatch** | Every API call logged; ingestion freshness and failure alarms |
| Raw preservation | **S3 Bronze**, immutable, partitioned | Full replay capability if a downstream bug is found months later |

### Phase 2 — Bronze → Silver

| Your capability | AWS service | Why this one |
|---|---|---|
| Automated data quality validation | **AWS Glue Data Quality (DQDL)** | Your business rules become executable code — see below |
| Cleansing, normalization, standardization | **AWS Glue Spark** | Scales to the volume; same PySpark logic you already write |
| SCD Type 2 historical tracking | **Iceberg `MERGE`** on S3 Silver | Row-level upserts on immutable object storage |
| Exception handling | **Quarantine prefix** + DQ outcome routing | One bad record never fails a job processing millions |
| DQ scoring | Glue DQ score written as a column / metric | Score travels with the data, visible at the approval gate |
| Bronze → Silver lineage | Glue lineage + SageMaker Catalog | Required evidence for the governance gate |

**Your business rules, expressed as DQDL:**

```
Rules = [
    IsComplete "impressions",
    ColumnValues "impressions" >= 0,
    ColumnValues "cost" >= 0,
    IsComplete "revenue"
]
```

This is the single strongest detail in the whole design. The business rules stated by stakeholders are not buried in a Spark script — they are declarative, version-controlled, independently auditable, and produce a pass/fail score that goes straight into the approval pack.

DQDL also supports **labels**, so each rule can be tagged with owning team, criticality, and SLA — useful when five teams each own different rules.

### Phase 3 — Silver → Gold

| Your capability | AWS service | Why this one |
|---|---|---|
| Business transformation, ROI modelling | **Glue / EMR Spark** | Aggregations, derived metrics, dimensional modelling |
| AI/ML feature preparation | **SageMaker Feature Store** | Point-in-time-correct feature retrieval — prevents label leakage in training |
| Embeddings for AI consumption | **S3 Vector buckets** | Similarity search without standing up a vector database |
| Gold-layer schema optimization | **Iceberg** partitioning + compaction | Query performance holds as the table grows |
| Data product versioning | **Iceberg snapshots** + SageMaker Catalog data products | Every approved version is reproducible |
| **Approval loop** | **SageMaker Catalog** publish → subscribe → approve | See below — this is the important one |
| Governed serving | **Lake Formation** grants issued on approval | Access is a consequence of approval, not a separate manual step |

---

## The approval gate is a real AWS service, not a manual process

This is the part of your architecture most portfolio projects never show, and AWS has a native fit for it.

**Amazon DataZone is now Amazon SageMaker Catalog**, inside SageMaker Unified Studio. It provides:

- **Data products** — group related assets into a business-aligned package, published as a unit
- **Subscription request workflow** — a consuming team requests access; a designated approver reviews
- **Approval → automatic Lake Formation grant** — when the CDO or Product Leadership approves, SageMaker Unified Studio issues the underlying Lake Formation permissions automatically
- **Metadata enforcement rules** — a data product cannot be published unless required business metadata is filled in. This turns your governance gate into an enforced control rather than a convention
- **Column-level lineage** and **data quality surfacing** — the evidence pack for the review meeting is generated, not assembled by hand

**Why this matters for the design:** your Phase 3 rejection loop (*"if stakeholders request additional data elements → re-transform → re-submit → approval"*) maps directly onto publish → subscription request → reject → revise → republish. It is a supported workflow, not something bolted on.

---

## Design decisions worth defending in review

**1. Masking happens on write, not on read.**
Applying masking in the Firehose Lambda transform means Bronze never physically stores the raw salary value. The alternative — storing raw and masking at query time via Lake Formation — is simpler to build but means the sensitive value exists on disk. For salary and PII, write-time masking is the stronger control. Trade-off: you cannot recover the original value later, so anything needing reversibility must be tokenised rather than masked.

**2. Quarantine, not fail-fast.**
A single malformed record must not fail a job processing millions of rows. Failed records are written to a quarantine prefix with the rejection reason attached, and the job completes. The **quarantine rate becomes the monitored metric** — a spike means a producer changed their payload without telling anyone.

**3. Bronze is immutable and never skipped.**
Every consumer reads Silver or Gold, never Bronze directly. Bronze exists solely as the replay layer. If a transformation bug is discovered six months out, Silver and Gold are rebuilt from Bronze rather than being lost.

**4. Approval gates block promotion, not development.**
Data Engineering can build and iterate on Gold candidates freely. What the gate controls is *promotion into the serving layer*. This keeps governance from becoming a bottleneck on engineering work.

---

## Open decisions before the deck

Three things worth settling first, because they change the slides:

1. **Deliverable at each gate.** "Data summary, quality results, schema design" is close — naming the artifact precisely (a **data contract**? a **DQ scorecard**? a **schema spec**?) makes the gate concrete rather than aspirational.

2. **Glue vs Databricks for Phase 2/3 processing.** The blueprint shows Glue for a fully AWS-native story. If the org already runs Databricks, that swaps in cleanly without changing anything else in the architecture — worth deciding which story the deck tells.

3. **SLA per phase.** How fresh must Bronze be? How often does Silver rebuild? Governance gates are approval-driven, but the pipelines underneath still need stated targets.

---

## Core architectural principle

> *"Ingest once, govern continuously, standardize progressively, approve explicitly, and serve trusted data from the Gold layer."*
