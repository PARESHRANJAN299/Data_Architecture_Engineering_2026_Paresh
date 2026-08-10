# Architecture Approval Gates

## Gate 0 — Design authorization

- [ ] Business problem and first use case approved
- [ ] Source terms, data classification, and owner recorded
- [ ] NFRs and proposed SLOs reviewed
- [ ] Alternatives and ADRs approved
- [ ] Threat model and cost envelope reviewed
- [ ] No implementation contains production credentials or data

## Gate 1 — Phase 1 production readiness

- [ ] Terraform deploys a clean environment
- [ ] Contract compatibility tests pass
- [ ] Load, burst, and hot-partition tests pass
- [ ] Source disconnect and ECS task failure recovery measured
- [ ] Partial Kinesis failures and throttling handled
- [ ] Quarantine and DLQ redrive demonstrated
- [ ] Accepted-event reconciliation passes
- [ ] IAM/KMS/Secrets Manager controls reviewed
- [ ] CloudWatch dashboard and actionable alarms exist
- [ ] Runbook and ownership rotation approved
- [ ] Unit cost measured and budget alarm tested

## Gate 2 — Phase 2 trusted-data readiness

- [ ] Bronze is immutable and replayable
- [ ] Source-to-Bronze reconciliation passes
- [ ] Silver is reproducible and idempotent
- [ ] Late, duplicate, corrupt, and schema-change cases tested
- [ ] Data quality thresholds and steward assigned
- [ ] Retention, lineage, and restricted raw access verified

## Gate 3 — Phase 3 consumption and AI readiness

- [ ] Gold metrics have business ownership and versioned definitions
- [ ] Query freshness, performance, concurrency, and cost pass
- [ ] Lake Formation access tests pass
- [ ] Lineage reaches the source contract
- [ ] ML/AI dataset and intended use approved
- [ ] Evaluation, privacy, monitoring, and human oversight approved

Approval requires links to evidence; a checked box without evidence is not a pass.
