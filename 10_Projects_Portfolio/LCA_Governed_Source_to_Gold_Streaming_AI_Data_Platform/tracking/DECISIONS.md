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
