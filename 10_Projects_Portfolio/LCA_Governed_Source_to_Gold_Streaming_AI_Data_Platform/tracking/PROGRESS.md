# Build Progress Log

**Project:** LCA Governed Source-to-Gold Streaming & AI Data Platform
**Owner:** Paresh Ranjan Rout
**Build start:** 9 August 2026

Dated record of what was actually built, in order, with evidence. One entry per meaningful milestone — not a to-do list.

---

## Entry 1 — Architecture designed and approved for build

**Date:** 9 August 2026
**Phase:** Design
**Status:** ✅ Complete

- Three-phase architecture defined: Source → Bronze → Silver → Gold, with formal governance gates between Silver and Gold
- AWS service mapping completed for every capability (see [`docs/aws-blueprint.md`](../docs/aws-blueprint.md))
- Blueprint diagram produced
- Core principle established: *"Ingest once, govern continuously, standardize progressively, approve explicitly, and serve trusted data from the Gold layer."*

**What this establishes:** the design is settled before any infrastructure is created, so build work is execution rather than exploration.

---

## Entry 2 — (next)

**Phase:** Phase 1 — Source → Bronze
**Status:** ⬜ Not started

Planned:
- S3 bucket structure with Bronze/Silver/Gold prefixes
- IAM roles, least-privilege scoped per phase
- Glue Schema Registry: register the canonical event schema
- Kinesis Data Stream + Firehose delivery to Bronze
- Lambda transform for column masking on write
- Verify: a raw salary value never appears in Bronze

---

## How to use this log

Each entry records:
1. **Date and phase**
2. **What was built** — concrete, not aspirational
3. **Evidence** — screenshot, ARN, S3 path, or job run ID
4. **What it establishes** — one line on why this milestone matters

Errors encountered go in [`ERRORS.md`](ERRORS.md), not here. Decisions and their reasoning go in [`DECISIONS.md`](DECISIONS.md).
## Entry 2 — Chat interaction source locked; ingestion design complete

**Date:** 10 August 2026
**Phase:** Phase 1 — Source → Bronze
**Status:** 🟡 Design complete, infrastructure not yet built

### Decided
- Canonical source for Entry 2: **chat interaction events** (marketing/campaign data remains planned as a second source for the multi-source expansion, not the initial build)
- Ingestion pattern: **outbox / durable staging** — Application -> masking Lambda -> DynamoDB -> Fargate poller -> Kinesis -> S3 Bronze
- Confirmed via whiteboard review: Kinesis never pulls from DynamoDB; Fargate is the only active agent moving data between the two

### Built (design artifacts)
- [x] Chat interaction event mapped into the existing canonical envelope — see `canonical-event-schema.md`
- [x] DynamoDB table design with required GSI for the poller's query pattern — see `dynamodb-table-design.md`
- [x] Write-time masking/tokenization Lambda logic — see `scripts/masking_lambda.py`
- [x] IAM roles scoped for all three components (masking Lambda, DynamoDB writer, Fargate poller) — see `infrastructure/iam-roles.md`
- [x] D-004 logged: tokenize `user_id` (reversible), mask free-text PII (irreversible) — these are not the same operation

### What this proves
The canonical envelope designed for a hypothetical multi-source future already fits a completely different, real event shape (chat interactions) without modification — the payload changes, the envelope doesn't. That's the actual validation of the "one standard schema" principle from the architecture doc.

### Not yet started
- [ ] Create the DynamoDB table in AWS (per the design doc)
- [ ] Create the KMS key for tokenization
- [ ] Deploy the masking Lambda
- [ ] Create the Kinesis Data Stream
- [ ] Build and deploy the Fargate poller service
- [ ] Attach all three IAM roles
- [ ] End-to-end test: one interaction, from raw event to a record sitting in S3 Bronze
- [ ] Verify: raw `user_id` never appears anywhere at rest; PII patterns in free text are masked
