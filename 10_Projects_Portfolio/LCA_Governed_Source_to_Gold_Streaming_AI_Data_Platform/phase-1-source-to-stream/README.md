# Phase 1 — Governed Source to Stream

**Goal:** prove that one external real-time source can be connected, contracted, secured, observed, recovered, and delivered to Kinesis without unexplained loss.

## Selected baseline

```text
Market-data WebSocket/API
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

1. Confirm the source's authentication, terms, rate limits, ordering, replay, and reconnect behavior.
2. Finalize the canonical contract and partition-key ADR.
3. Write local contract tests with synthetic/public sample events.
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

## Definition of done

- all Gate 1 controls in [`../governance/phase-gates.md`](../governance/phase-gates.md) pass with linked evidence;
- the accepted-event lifecycle is explainable;
- a second consumer can replay from Kinesis without changing the producer;
- the architecture can be redeployed from source control;
- operations can detect and recover every tested failure;
- cost per million accepted events is measured;
- no sensitive values exist in Git, images, logs, or evidence.
