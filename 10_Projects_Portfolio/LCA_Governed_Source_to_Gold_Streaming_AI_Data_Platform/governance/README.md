# Governance

Cross-cutting controls that apply to **every** phase, not a stage at the end.

## Control areas

| Area | Implementation |
|---|---|
| Data security | IAM, KMS encryption, VPC endpoints |
| Access control | IAM roles + Lake Formation tag-based access control (LF-TBAC) |
| Data quality | AWS Glue Data Quality (DQDL rulesets) |
| Metadata | Glue Data Catalog, SageMaker Catalog |
| Data lineage | Column-level lineage across Bronze → Silver → Gold |
| Schema governance | Glue Schema Registry, validation on write |
| PII discovery | Amazon Macie scheduled scans |
| Auditability | CloudTrail |
| Monitoring | CloudWatch — freshness SLAs, quarantine rate alarms |
| Approval | SageMaker Catalog publish / subscribe / approve workflow |

## Why tag-based access control

With multiple consuming teams, writing individual grants per team per table does not scale. Columns are tagged (`pii=true`, `domain=finance`) and access is granted against **tags** rather than individual tables. Adding a new table with existing tags requires no new grants.

## Approval gates

| Gate | Point in flow | Approvers | Artifact submitted |
|---|---|---|---|
| **Gate 1** | Silver → Phase 3 | Senior Data Stakeholders, CDO, Product Leadership | Schema, business rules, DQ results, lineage |
| **Gate 2** | Gold candidate → serving | CDO, Product Leadership | Data product spec, metrics definitions, sample output, lineage |

Templates and completed approval records live in [`approval-gates/`](approval-gates/).

## Data contracts

Agreements between data producers and the platform: expected schema, delivery frequency, ownership, and what constitutes a breaking change. See [`data-contracts/`](data-contracts/).

Purpose: a producer changing their payload without notice is the single most common cause of silent pipeline breakage. The contract makes that change a violation rather than a surprise.
