# Phase 3 — Silver → Gold

**AI/ML-Optimized Data Products & Governed Serving**

**Status:** ⬜ Not started

## Objective

Transform approved Silver data into high-quality, consumption-ready data products optimized for Product ROI, Analytics, and AI/ML model execution — and serve them only after explicit approval.

## Capabilities delivered

- Business-focused data transformation
- AI/ML-ready feature and metric preparation
- Product ROI and Marketing analytics datasets
- Required dimensions, measures, attributes, derived metrics
- Business-level aggregations and summaries
- AI / semantic model alignment
- Gold-layer schema optimization
- Data product versioning and governance
- End-to-end lineage and traceability

## AWS services

| Capability | Service |
|---|---|
| Business transformation | AWS Glue Spark, Amazon EMR |
| Feature preparation | SageMaker Feature Store (point-in-time correct) |
| Embeddings | S3 Vector buckets |
| Schema optimization | Iceberg partitioning and compaction |
| Data product versioning | Iceberg snapshots, SageMaker Catalog |
| Governed serving | Lake Formation grants issued on approval |

## Governance Gate 2 and the approval loop

```
Silver → transformation → GOLD CANDIDATE → stakeholder review
                                              │
                    ┌─────────── REJECTED ────┤
                    │                          │
                    ▼                          ▼
        add columns / re-transform         APPROVED
        re-validate / re-submit               │
                    │                          ▼
                    └──────────────►  Governed Gold Serving Layer
```

A Gold candidate is **versioned but not served**. It becomes consumable only after the CDO and Product Leadership approve. Rejection is a normal path, not a failure — feedback returns to Data Engineering, the data is reprocessed, and the product is resubmitted. This cycle repeats until approved.

Once approved, the Gold Serving Layer is the **single governed consumption layer**. Product, Marketing, Analytics, BI, and AI/ML consume exclusively from it.

## Output

**Approved Gold Data Product** served through the governed consumption layer.

## Build checklist

- [ ] Business transformation logic written
- [ ] ROI and derived metrics implemented per stakeholder specification
- [ ] SageMaker Feature Store populated with point-in-time-correct features
- [ ] Embeddings generated and written to S3 Vector bucket
- [ ] Gold candidate versioned as an Iceberg snapshot
- [ ] Data product published to SageMaker Catalog
- [ ] Submitted to Gate 2
- [ ] Approval received, Lake Formation grants issued
- [ ] Consumer access verified per team
