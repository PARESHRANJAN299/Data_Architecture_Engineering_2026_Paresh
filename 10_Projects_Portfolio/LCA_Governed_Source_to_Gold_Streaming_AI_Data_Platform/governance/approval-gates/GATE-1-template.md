# Governance Gate 1 — Silver Model Approval

**Submitted by:** Paresh Ranjan Rout (Data Engineering)
**Submission date:**
**Decision:** ⬜ Approved   ⬜ Rejected — revisions requested

## Approvers

| Role | Name | Decision | Date |
|---|---|---|---|
| Senior Data Stakeholder | | | |
| Chief Data Officer | | | |
| Product Leadership | | | |

## 1. Silver data model

Table name:
Format: Apache Iceberg
Partitioning:
Row count:

Schema summary:

| Column | Type | Nullable | Business meaning |
|---|---|---|---|
| | | | |

## 2. Business rules applied

| Rule | Expressed as | Pass rate |
|---|---|---|
| Impressions must be non-null | `IsComplete "impressions"` | |
| Impressions must be non-negative | `ColumnValues "impressions" >= 0` | |
| Cost must be non-negative | `ColumnValues "cost" >= 0` | |
| Revenue must be non-null | `IsComplete "revenue"` | |

## 3. Data quality results

Overall DQ score:
Records processed:
Records quarantined:
Quarantine rate:

Top quarantine reasons:

## 4. SCD Type 2 coverage

Dimensions tracked historically:
Verification that a point-in-time query returns historical, not current, values:

## 5. Lineage

Bronze → Silver lineage captured: ⬜ Yes  ⬜ No
Link / screenshot:

## 6. Reviewer comments

## 7. Required changes before resubmission

