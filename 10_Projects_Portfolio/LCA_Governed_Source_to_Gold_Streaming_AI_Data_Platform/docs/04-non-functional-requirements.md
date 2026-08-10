# Non-Functional Requirements and Proposed SLOs

These are design targets for validation. A target becomes an achieved SLO only after monitoring evidence exists.

## Phase 1 proposed service levels

| Dimension | Proposed target | Measurement |
|---|---|---|
| Accepted-event accountability | 100% of accepted events are delivered, retrying, quarantined, or explicitly reconciled | Source/producer/Kinesis counters and reconciliation job |
| Ingress latency | p95 under 2 seconds from adapter receipt to Kinesis acknowledgement under test load | Embedded timestamps and CloudWatch metric |
| Adapter recovery | Healthy ingestion resumes within 5 minutes after an injected task failure | Failure-injection report |
| Source reconnect | Bounded exponential backoff with jitter; no retry storm | Connection-state metrics and logs |
| Coinbase heartbeat health | Stale heartbeat is detected within the approved test threshold | Last-heartbeat-age metric and alarm |
| Source gap accountability | Every detected Coinbase sequence gap is recovered or explicitly reported as unrecovered | Gap register and reconciliation evidence |
| Schema enforcement | 100% of published events pass the registered contract | Producer validation metric |
| Invalid-event handling | 100% quarantined with safe reason and correlation ID | Quarantine inventory |
| Duplicate safety | Duplicate input does not change final Silver result | Phase 2 idempotency test |
| Infrastructure reproducibility | Clean environment deploys from version-controlled IaC | CI plan/apply evidence |
| Security | No long-lived credentials in code, image, state output, or logs | Secret scanning and access review |
| Cost visibility | Cost allocation tags and monthly budget alarms present before load testing | Billing tags and budget evidence |

## Reliability model

- Delivery semantics: at least once.
- Ordering scope: within the selected partition key; never global.
- Recovery source: Kinesis retention after acceptance; Coinbase REST recovery before acceptance where available and provable; Bronze after Phase 2.
- Source limitation: Coinbase REST recovery is best-effort and must never be represented as guaranteed complete historical replay.
- RPO proposal for accepted events: zero unexplained loss in controlled failure tests.
- RTO proposal for a single adapter task failure: five minutes.
- Poison records: quarantine or DLQ; never block the healthy flow indefinitely.

## Performance model

Capture these inputs before selecting final capacity:

- average and peak events per second;
- average, p95, and maximum record size;
- burst duration and daily volume;
- partition-key cardinality and skew;
- required number of independent consumers;
- producer acknowledgement latency;
- retention and replay window;
- compression ratio and S3 object-size targets.

Load tests must include normal, burst, hot-key, throttling, reconnect, malformed-message, and duplicate scenarios.

## Security requirements

- least-privilege roles per workload function;
- temporary credentials through task roles;
- Secrets Manager for source secrets;
- encryption in transit and at rest;
- KMS key policies separated from workload policies;
- CloudTrail and configuration-change evidence;
- no public S3 buckets;
- no sensitive payloads in logs, metrics, tags, or DLQ attributes;
- image and dependency scanning before deployment;
- explicit break-glass process with time-bound review.

## Observability requirements

Every event carries `event_id`, `correlation_id`, source time, ingestion time, schema version, and source. Dashboards and alarms cover:

- connection status and reconnect count;
- last Coinbase heartbeat age and detected sequence gaps;
- events received, accepted, rejected, retried, and failed;
- `PutRecords` partial failures and throttling;
- Kinesis incoming records/bytes and iterator age when consumers begin;
- DLQ depth and oldest-message age;
- quarantine rate by reason;
- task restarts, CPU, memory, and network;
- schema-version distribution;
- cost and utilization indicators.

## Cost guardrails

- mandatory `Project`, `Environment`, `Owner`, `CostCenter`, and `DataClassification` tags;
- AWS Budget alerts before load testing;
- on-demand Kinesis initially, followed by measured comparison with provisioned capacity;
- S3 lifecycle and retention policies by zone;
- log retention explicitly configured;
- non-production schedules where safe;
- unit economics reported as cost per million accepted events and cost per retained GB.
