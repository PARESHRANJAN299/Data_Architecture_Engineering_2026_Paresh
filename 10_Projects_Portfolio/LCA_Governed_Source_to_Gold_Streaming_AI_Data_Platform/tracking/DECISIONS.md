# Decision Log

**Project:** LCA Governed Source-to-Gold Streaming & AI Data Platform
**Owner:** Paresh Ranjan Rout

Significant architectural and implementation decisions, with the reasoning and the trade-off accepted. Anything that a reviewer might reasonably question belongs here.

---

## D-001 — Column masking applied on write, not on read

**Date:** 9 August 2026
**Status:** Accepted

**Decision:** Sensitive columns (salary, PII) are masked in the Firehose Lambda transform before the record lands in Bronze.

**Alternative considered:** Store raw in Bronze, apply masking at query time via Lake Formation column-level security.

**Reasoning:** Write-time masking means the raw value never physically exists on disk. Read-time masking is easier to build and is reversible, but the sensitive value remains recoverable by anyone with direct S3 access.

**Trade-off accepted:** Masked values cannot be recovered. Any field that may legitimately need recovery later must be *tokenised* (reversible with a key) rather than masked.

---

## D-002 — Quarantine on failure, not fail-fast

**Date:** 9 August 2026
**Status:** Accepted

**Decision:** Records failing data quality validation are written to a quarantine prefix with the rejection reason attached. The job completes successfully.

**Alternative considered:** Fail the job on any validation error.

**Reasoning:** A single malformed record should not stop a job processing millions of rows. Quarantining preserves both throughput and the failed records for investigation.

**Trade-off accepted:** Bad data is silently excluded unless someone watches the quarantine rate. Mitigation: quarantine rate is an alarmed CloudWatch metric — a spike indicates a producer changed their payload without notice.

---

## D-003 — Bronze is never consumed directly

**Date:** 9 August 2026
**Status:** Accepted

**Decision:** All consumers read from Silver or Gold. Bronze exists solely as the immutable replay layer.

**Reasoning:** Guarantees that a transformation defect discovered later can be corrected by rebuilding downstream layers, rather than leaving permanently incorrect data.

**Trade-off accepted:** Storage cost of retaining raw data indefinitely. Mitigation: S3 lifecycle policy moves Bronze partitions older than the agreed retention window to a colder storage class.

---

## Template

### D-00N — decision title

**Date:**
**Status:** Proposed | Accepted | Superseded

**Decision:**
**Alternative considered:**
**Reasoning:**
**Trade-off accepted:**
## D-004 — Tokenize identifiers, mask free text (refinement to ADR-001)

**Date:** 10 August 2026
**Status:** Accepted

**Context:** Building the chat-interaction schema surfaced a distinction ADR-001 didn't originally make: "masking" was used as one blanket term, but two different fields need two different treatments.

**Decision:**
- `user_id` -> **tokenized** (reversible, KMS-held key)
- PII found inside free text (`user_question`, `generated_answer`) -> **masked** (irreversible)

**Reasoning:** the platform has a legitimate ongoing need to group interactions by the same user (session analysis, personalization, support lookback) — a one-way mask on `user_id` would silently break that capability. Free text is different: if a user types their email into a chat message, there is no legitimate downstream reason to ever recover that exact string.

**Trade-off accepted:** tokenization requires managing a KMS key and an access policy for who can decrypt (a separate, narrower permission than tokenizing) — more operational surface than a flat mask, accepted because the capability it preserves is required.
