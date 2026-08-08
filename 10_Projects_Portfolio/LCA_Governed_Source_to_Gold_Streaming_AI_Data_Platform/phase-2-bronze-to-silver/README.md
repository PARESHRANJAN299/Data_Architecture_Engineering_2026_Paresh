# Phase 2 — Bronze → Silver

**Data Quality, Cleansing, Standardization & Historical Modeling**

**Status:** ⬜ Not started

## Objective

Convert Bronze data into trusted, validated, standardized, business-ready data — then submit it for formal approval before it may progress.

## Capabilities delivered

- Automated data quality validation
- Data cleansing and normalization
- Business-rule validation
- Schema standardization to the enterprise canonical model
- Product and Marketing semantic standardization
- AI/analytics data requirement alignment
- SCD Type 2 historical dimension tracking
- Data quality scoring and exception handling
- Bronze → Silver lineage capture

## Business rules as code

Stakeholder rules are expressed in DQDL so they are version-controlled, auditable, and automatically scored. See [`data-quality/`](data-quality/).

```
Rules = [
    IsComplete "impressions",
    ColumnValues "impressions" >= 0,
    ColumnValues "cost" >= 0,
    IsComplete "revenue"
]
```

## AWS services

| Capability | Service |
|---|---|
| Cleansing, normalization, standardization | AWS Glue Spark |
| Data quality validation and scoring | AWS Glue Data Quality (DQDL) |
| SCD Type 2 | Apache Iceberg `MERGE` |
| Exception handling | Quarantine prefix on S3 |
| Lineage | Glue Data Catalog, SageMaker Catalog |

## Governance Gate 1

Before any data progresses to Phase 3, the following is submitted for review by **Senior Data Stakeholders, the CDO, and Product Leadership**:

- Silver data model and schema
- Business rules applied
- Data quality results and score
- Bronze → Silver lineage

Templates and approval records: [`../governance/approval-gates/`](../governance/approval-gates/)

## Output

**Trusted Silver Layer** — clean, validated, standardized, historically consistent data.

## Build checklist

- [ ] Glue Spark standardization job written
- [ ] DQDL ruleset registered against the Silver table
- [ ] Quarantine routing implemented and tested with a deliberately bad record
- [ ] SCD Type 2 merge logic implemented
- [ ] DQ score surfaced and attached to the dataset
- [ ] Lineage verified in the catalog
- [ ] Approval pack assembled and submitted to Gate 1
