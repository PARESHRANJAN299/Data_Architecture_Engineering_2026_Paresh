# ADR-001 — Column masking applied on write, not on read

**Status:** Accepted
**Date:** 9 August 2026
**Decision owner:** Paresh Ranjan Rout

## Context

The platform ingests source data containing sensitive attributes, including salary and PII. These must not be visible to unauthorised consumers. AWS offers two viable approaches, applied at different points in the flow.

## Options considered

**Option A — mask on write.** Apply masking in the Firehose Lambda transformation, before the record is written to Bronze.

**Option B — mask on read.** Store raw values in Bronze, apply Lake Formation column-level security so unauthorised consumers cannot select the column.

## Decision

Option A — mask on write.

## Reasoning

Under Option B, the raw sensitive value physically exists in S3. Anyone with direct bucket access, or any misconfiguration of Lake Formation policy, exposes it. Under Option A, the raw value never lands, so there is nothing on disk to expose.

For salary and PII specifically, the stronger guarantee justifies the reduced flexibility.

## Trade-offs accepted

- **Irreversibility.** A masked value cannot be recovered. Any field that may legitimately need recovery later must be *tokenised* (reversible with a KMS-held key) rather than masked outright.
- **Bronze is no longer a byte-exact copy of source.** This weakens the pure replay guarantee for those specific columns. Accepted, because replay of a masked column would only ever reproduce the mask.
- **Transformation cost at ingest.** The Lambda transform adds per-record processing and cost to the ingestion path.

## Consequences

- The masking function becomes a critical path component and requires its own testing and monitoring.
- Any change to which columns are masked requires a change to the Lambda, not just a policy update.
- Verification step added to Phase 1 checklist: confirm no raw sensitive value appears in Bronze.
