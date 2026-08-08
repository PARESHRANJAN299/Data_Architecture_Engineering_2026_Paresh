# Phase 1 — Source → Bronze

**Secure CDC-Based Streaming Ingestion & Data Governance**

**Status:** ⬜ Not started

## Objective

Establish a secure, automated foundation for continuous data ingestion, where sensitive data is protected before it ever lands and raw data is preserved for replay.

## Capabilities delivered

- Real-time / near-real-time streaming ingestion
- CDC (Change Data Capture) for incremental loading
- Automated ingestion and pipeline orchestration
- Source-to-Bronze schema management and validation
- Sensitive-data protection via column-level masking on write
- PII / confidential attribute governance
- Data lineage and metadata capture
- Auditability and ingestion monitoring
- Raw data preservation under governed access

## AWS services

| Capability | Service |
|---|---|
| CDC from relational sources | AWS DMS (CDC mode) |
| Streaming ingestion | Kinesis Data Streams |
| Device / telemetry ingestion | AWS IoT Core → Kinesis |
| Delivery to S3 | Amazon Data Firehose |
| Schema validation on write | Glue Schema Registry |
| Column masking before landing | Firehose → Lambda transformation |
| Encryption | KMS, VPC endpoints |
| PII discovery | Amazon Macie |
| Catalog & lineage | Glue Data Catalog |
| Audit & monitoring | CloudTrail, CloudWatch |

## Bronze layer contract

- **Immutable.** Records are never updated or deleted in place.
- **Partitioned** `source=/year=/month=/day=/hour=`
- **Masked on arrival.** No raw salary or PII value is written to disk.
- **Never consumed directly.** Bronze serves replay only.

## Output

**Governed Bronze Layer** — secure, incrementally loaded, source-aligned data.

## Build checklist

- [ ] S3 bucket and prefix structure created
- [ ] IAM roles created, least-privilege scoped
- [ ] Canonical schema registered in Glue Schema Registry
- [ ] Kinesis Data Stream provisioned
- [ ] Lambda masking transform written and tested
- [ ] Firehose delivery stream configured with transform attached
- [ ] DMS CDC task configured for relational source
- [ ] Verification: confirm no raw sensitive value present in Bronze
- [ ] CloudWatch freshness alarm configured
