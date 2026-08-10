# Phase 1 — Governed Source to Stream

**Goal:** prove that one external real-time source can be connected, contracted, secured, observed, recovered, and delivered to Kinesis without unexplained loss.

## Selected baseline

```text
Coinbase Advanced Trade public WebSocket
market_trades + heartbeats | BTC-USD + ETH-USD
        ↓
ECS Fargate source adapter
        ↓
Canonical JSON event + Glue Schema Registry
        ↓
Amazon Kinesis Data Streams

Invalid contract     → encrypted S3 quarantine
Delivery exhausted   → encrypted SQS DLQ
Checkpoints/control  → DynamoDB
Secrets              → Secrets Manager
Metrics/logs/alarms  → CloudWatch
Audit                → CloudTrail
Infrastructure       → Terraform + CI/CD
```

## Build order

1. Confirm Coinbase terms, current rate limits, message schema, ordering, recovery, and reconnect behavior against official documentation.
2. Finalize the canonical contract and partition-key ADR.
3. Write local contract tests with captured Coinbase fixtures plus synthetic invalid, duplicate, and gap cases.
4. Build the containerized source adapter without AWS dependencies.
5. Add Kinesis producer batching, partial-failure retry, backoff, and metrics.
6. Provision the AWS environment through Terraform.
7. Add quarantine, DLQ, Secrets Manager, IAM, KMS, CloudWatch, and CloudTrail.
8. Execute load and failure tests.
9. Publish evidence and request Gate 1 approval.

## Phase 1 backlog

```text
src/                     source adapter and canonicalization
tests/                   unit, contract, load and failure tests
infra/terraform/         network, ECS, Kinesis, SQS, S3, DynamoDB, IAM, KMS
observability/           dashboards, alarms and queries
runbooks/                reconnect, throttle, DLQ, quarantine and rollback
evidence/                generated test and review outputs
```

These implementation directories will be created incrementally. Empty scaffolding is intentionally avoided.

## Locked adapter rules

- connect to `wss://advanced-trade-ws.coinbase.com`;
- subscribe to `market_trades` and `heartbeats` for `BTC-USD` and `ETH-USD`;
- publish one canonical event per trade, not one event per WebSocket message;
- use `coinbase.market_trade.{product_id}.{trade_id}` as the deterministic event ID;
- use `coinbase.advanced_trade#{product_id}` as the Kinesis partition key;
- convert heartbeats into health metrics rather than business events;
- treat REST recovery as best-effort and emit a gap report when recovery cannot be proven;
- defer `level2` order-book state until the market-trade path passes Gate 1.

See [`coinbase-source-specification.md`](coinbase-source-specification.md) for the source-to-contract mapping.

## Definition of done

- all Gate 1 controls in [`../governance/phase-gates.md`](../governance/phase-gates.md) pass with linked evidence;
- the accepted-event lifecycle is explainable;
- a second consumer can replay from Kinesis without changing the producer;
- the architecture can be redeployed from source control;
- operations can detect and recover every tested failure;
- cost per million accepted events is measured;
- no sensitive values exist in Git, images, logs, or evidence.
