# Phase 2 — Bronze to Silver Roadmap

Implementation begins only after Gate 1.

## Outcome

- Amazon Data Firehose delivers encrypted, compressed, partitioned Bronze objects.
- Bronze retains the canonical envelope and original source payload.
- Glue Catalog makes datasets discoverable.
- Glue/Spark produces Silver Iceberg tables.
- Silver standardizes types and time, deduplicates, validates, and records quality outcomes.
- Any transformation can be rerun deterministically from Bronze.

## Core evidence

- source/Kinesis/Bronze count reconciliation;
- S3 object-size and partition-health report;
- schema-evolution tests;
- late and out-of-order event tests;
- duplicate and corrupt-record tests;
- Silver quality score and failed-row quarantine;
- replay and backfill runbook;
- cost per retained and processed GB.
