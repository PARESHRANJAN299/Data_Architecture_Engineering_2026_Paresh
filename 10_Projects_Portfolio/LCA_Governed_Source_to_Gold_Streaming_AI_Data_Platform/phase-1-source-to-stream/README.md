# Phase 1 — Governed Source to Stream

**Status:** 🟠 IN PROGRESS

**Goal:** prove that one external real-time source can be connected, contracted, secured, observed, recovered, and delivered to Kinesis without unexplained loss.

## Selected baseline

```text
Coinbase Advanced Trade public WebSocket
market_trades + heartbeats | BTC-USD + ETH-USD
        ↓
ECS Fargate source adapter
        ↓
Unchanged Coinbase source JSON
        ↓
Amazon Kinesis Data Streams

Unparseable transport → encrypted S3 quarantine
Delivery exhausted   → encrypted SQS DLQ
Checkpoints/control  → DynamoDB
Secrets              → Secrets Manager
Metrics/logs/alarms  → CloudWatch
Audit                → CloudTrail
Infrastructure       → Terraform + CI/CD
```

## Build order

| Step | Work item | Status | Required completion evidence |
|---:|---|---|---|
| 1 | Confirm Coinbase terms, endpoint, channels, products, rate limits and recovery limits | ✅ ACHIEVED | ADR-004, source specification and authoritative references |
| 2 | Finalize raw transport rules and target Silver mapping | ✅ ACHIEVED | JSON/YAML checks and reviewed mapping specification |
| 3 | Connect locally and capture sanitized source fixtures | ✅ ACHIEVED | Curated fixtures plus bounded live capture: 20 market messages, 230 trades, 10 heartbeats, both products, 0 gaps/quarantine |
| 4 | Build and containerize the source adapter | ✅ ACHIEVED | 12 unit/contract tests, raw-preservation proof, non-root image and live container smoke test |
| 5 | Add and prove the Kinesis producer | 🟠 IN PROGRESS | Local sink tests and manual stream write/read passed; application delivery, retry and reconciliation remain |
| 6 | Provision the AWS environment through Terraform | ⬜ NOT STARTED | Validated plan, security scan and deployment evidence |
| 7 | Add quarantine, DLQ, IAM, KMS, DynamoDB, CloudWatch and CloudTrail | ⬜ NOT STARTED | Access, redrive, alarm and audit evidence |
| 8 | Execute load, reconnect, gap, duplicate, throttle and task-failure tests | ⬜ NOT STARTED | Failure-test report with measured SLO results |
| 9 | Publish the evidence package and request Gate 1 approval | ⬜ NOT STARTED | Every Gate 1 control linked to passing evidence |

Completed architecture or contract design is not treated as proof that the runtime works. A step changes to achieved only after its required evidence is committed.

## Phase 1 backlog

```text
src/                     source adapter and raw transport
tests/                   unit, contract, load and failure tests
infra/terraform/         network, ECS, Kinesis, SQS, S3, DynamoDB, IAM, KMS
observability/           dashboards, alarms and queries
runbooks/                reconnect, throttle, DLQ, quarantine and rollback
evidence/                generated test and review outputs
```

These implementation directories will be created incrementally. Empty scaffolding is intentionally avoided.

## Implemented local backend

```text
src/coinbase_adapter/config.py   validated endpoint, product and reliability configuration
src/coinbase_adapter/client.py   subscribe, receive, heartbeat-age monitoring and reconnect backoff
src/coinbase_adapter/handler.py  envelope checks, sequence diagnostics and unchanged raw routing
src/coinbase_adapter/sinks.py    development JSONL plus unchanged-message Kinesis `PutRecord` sink
tests/                           sanitized fixtures and 16 passing unit/contract tests
Dockerfile                      non-root local runtime
evidence/                       committed summaries without live payloads
```

Run locally:

```bash
make setup
make test
make smoke
```

The same `RawMessageSink` protocol now supports either the development JSONL destination or Kinesis. The Kinesis implementation sends one complete Coinbase source message as one `PutRecord` data blob. Local tests use a recording stub, so no AWS delivery claim is made yet.

Test only the Kinesis request contract without AWS credentials or AWS resource changes:

```bash
PYTHONPATH=src .venv/bin/python -m unittest tests.test_sinks -v
```

The future ECS task will select the AWS destination with:

```bash
python -m coinbase_adapter.main --kinesis-stream lca-coinbase-market-trades-dev
```

The ECS task role will supply temporary AWS credentials automatically. No access key belongs in the command, source code, image or GitHub.

Evidence: [`evidence/local-adapter-step-3-4.json`](evidence/local-adapter-step-3-4.json).
Kinesis sink evidence: [`evidence/local-kinesis-sink-test.json`](evidence/local-kinesis-sink-test.json).
Manual AWS smoke evidence: [`evidence/manual-kinesis-write-read-smoke-test.json`](evidence/manual-kinesis-write-read-smoke-test.json).

## Manual AWS infrastructure progress

The first AWS resource has now been configured manually in the AWS Management Console so each architecture decision can be learned and verified before it is automated.

| Resource or control | Status | Evidence |
|---|---|---|
| Kinesis stream `lca-coinbase-market-trades-dev` | ✅ ACHIEVED & VERIFIED | Active, provisioned, one shard, 24-hour retention; [redacted evidence](evidence/manual-kinesis-stream-creation.json) |
| Kinesis server-side encryption | ✅ ACHIEVED & VERIFIED | Update succeeded using AWS-managed `aws/kinesis` |
| Manual Kinesis write/read smoke test | ✅ ACHIEVED & VERIFIED | CloudShell returned shard/sequence/KMS; Data Viewer returned the expected record from `Trim horizon`; [redacted evidence](evidence/manual-kinesis-write-read-smoke-test.json) |
| ECS task and execution roles | ✅ ACHIEVED & VERIFIED | Trust verified; exact-stream allow and wildcard-deny simulations passed; [redacted evidence](evidence/manual-ecs-iam-foundation.json) |
| Kinesis `PutRecord` sink and local tests | ✅ ACHIEVED & VERIFIED — LOCAL | 4 focused tests and all 16 adapter tests passed; [evidence](evidence/local-kinesis-sink-test.json) |
| ECR repository and adapter image | ⬜ NOT STARTED | Versioned image and image-scan evidence required |
| ECS adapter deployment | ⬜ NOT STARTED | Runtime role assumption, task health and CloudWatch logs required |
| Coinbase-to-Kinesis live delivery | ⬜ NOT STARTED | Reconciliation, retry and unchanged JSON evidence required |

The complete manual configuration theory and tracker are maintained in [`../docs/07-phase-1-manual-aws-implementation.md`](../docs/07-phase-1-manual-aws-implementation.md). Architecture interview practice is maintained in the [`Kinesis/KMS guide`](../docs/08-kinesis-kms-architecture-interview-guide.md) and [`ECS IAM guide`](../docs/09-ecs-iam-architecture-interview-guide.md).

For the beginner-friendly distinction between the deployment path and data path, read [`../docs/10-ecs-ecr-fargate-simple-explainer.md`](../docs/10-ecs-ecr-fargate-simple-explainer.md).

For Data Engineer and Data Architect interview practice in Beginner, Medium and Company-scale Scenario modes, read [`../docs/11-ecs-ecr-fargate-data-engineering-architecture-interview-guide.md`](../docs/11-ecs-ecr-fargate-data-engineering-architecture-interview-guide.md).

## Locked adapter rules

- connect to `wss://advanced-trade-ws.coinbase.com`;
- subscribe to `market_trades` and `heartbeats` for `BTC-USD` and `ETH-USD`;
- publish one unchanged Coinbase `market_trades` message per Kinesis record;
- preserve nested event/trade arrays through Bronze;
- use a stable transport partition key derived from the subscribed product scope;
- convert heartbeats into health metrics rather than business events;
- treat REST recovery as best-effort and emit a gap report when recovery cannot be proven;
- defer trade explosion, standard column names, data types and quality rules to Silver;
- defer `level2` order-book state until the market-trade path passes Gate 1.

See [`coinbase-source-specification.md`](coinbase-source-specification.md) for the raw transport rules and target Silver mapping.

## Definition of done

- all Gate 1 controls in [`../governance/phase-gates.md`](../governance/phase-gates.md) pass with linked evidence;
- the accepted-event lifecycle is explainable;
- a second consumer can replay from Kinesis without changing the producer;
- the architecture can be redeployed from source control;
- operations can detect and recover every tested failure;
- cost per million accepted events is measured;
- no sensitive values exist in Git, images, logs, or evidence.
