# Three-Phase Delivery Roadmap

## Delivery model

Each increment follows the same loop:

```text
Problem → Requirements → Alternatives → ADR → Build → Failure test → Evidence → Gate
```

## Phase 1 — Source to Stream

### Increment 1: Event contract

- lock Coinbase Advanced Trade `market_trades` and `heartbeats` for `BTC-USD` and `ETH-USD`;
- record its ordering, batching, connection, and best-effort recovery behavior;
- create the canonical JSON Schema and sample events;
- define schema ownership and compatibility policy;
- implement local validation and contract tests.

### Increment 2: Source adapter

- containerize a minimal Coinbase WebSocket adapter;
- subscribe within the source connection window and monitor heartbeat age;
- fan out each trade in a Coinbase message to one canonical event;
- run it as an ECS Fargate service;
- use task roles and Secrets Manager;
- expose structured metrics without logging payloads.

### Increment 3: Streaming backbone

- provision Kinesis with Terraform;
- implement partition-key strategy and batch writes;
- handle partial failures, backoff, throttling, and duplicates;
- demonstrate retention and replay with a test consumer.

### Increment 4: Failure and recovery

- add S3 quarantine for invalid contracts;
- add SQS DLQ for exhausted delivery;
- add DynamoDB checkpoints/control state only where the use case proves it;
- execute reconnect, task-kill, throttling, duplicate, and malformed-event tests.
- execute Coinbase sequence-gap and stale-heartbeat tests.

### Increment 5: Production controls

- CI security and policy checks;
- CloudWatch dashboard and alarms;
- CloudTrail evidence and cost budget;
- runbook, operational ownership, and Phase 1 approval package.

## Phase 1 gate

Phase 2 cannot start until:

- the architecture and threat model are approved;
- source-to-Kinesis reconciliation passes;
- all failure scenarios have evidence;
- no secrets or sensitive payloads appear in Git or logs;
- infrastructure is reproducible;
- SLO dashboard and runbook exist;
- cost estimate and measured unit cost are documented.

## Phase 2 — Bronze to Silver

- configure Amazon Data Firehose to deliver compressed, partitioned Bronze objects;
- preserve original payload and event metadata;
- catalog Bronze data;
- create Silver Iceberg tables;
- standardize timestamps and types;
- deduplicate by event identity and ordering rules;
- isolate bad records and support deterministic replay;
- publish reconciliation and data-quality results.

## Phase 2 gate

- Bronze is immutable and replayable;
- source/Kinesis/Bronze counts reconcile within documented semantics;
- Silver is reproducible from Bronze;
- late, duplicate, and schema-evolution tests pass;
- permissions and retention are validated;
- quality ownership and incident response are assigned.

## Phase 3 — Silver to Gold, Analytics and AI

- define business-owned metrics and dimensional models;
- build versioned Gold products;
- select Athena or Redshift by workload evidence;
- publish QuickSight dashboards;
- implement Lake Formation access and lineage;
- add anomaly detection/forecasting only after data quality is proven;
- permit Bedrock/SageMaker access only through approved datasets and evaluations.

## Phase 3 gate

- business owner approves metric definitions;
- lineage traces metrics to source contracts;
- access tests prove least privilege;
- BI freshness, performance, and cost SLOs pass;
- ML/AI evaluation, drift, privacy, and human-oversight requirements pass.

## Evidence backlog

The portfolio should eventually contain:

- architecture and threat-model diagrams;
- ADRs and rejected alternatives;
- Terraform plans and CI results;
- schema compatibility tests;
- load and failure-injection reports;
- reconciliation and quality reports;
- CloudWatch dashboards and alarms;
- cost model and budget evidence;
- runbooks and incident simulations;
- lineage and access-control screenshots;
- business metric and AI evaluation approvals.
