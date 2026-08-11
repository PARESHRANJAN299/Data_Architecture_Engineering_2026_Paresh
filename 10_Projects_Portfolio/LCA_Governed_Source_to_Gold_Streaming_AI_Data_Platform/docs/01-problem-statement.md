# Problem Statement and Business Outcomes

**Owner:** Paresh Ranjan Rout
**Status:** Approved architecture baseline

## Business problem

Organizations receive continuously changing data from operational applications, public APIs, partners, devices, and business platforms. When each source is integrated independently, the organization accumulates:

- duplicate ingestion and retry code;
- inconsistent event identifiers, timestamps, and schemas;
- data loss or duplication that cannot be explained;
- undocumented transformations and metric definitions;
- slow onboarding of new sources;
- weak access controls and audit evidence;
- raw or sensitive data reaching dashboards and AI systems;
- high operating cost caused by overlapping tools and pipelines.

## Proposed solution

Create a governed, reusable AWS streaming platform with four stable interfaces:

1. **Source adapter interface** — connects to a source and transports the source message without business transformation.
2. **Raw streaming contract** — defines source, transport, ordering, timing and payload-preservation behavior.
3. **Medallion data contract** — preserves raw history and progressively promotes trustworthy data.
4. **Consumption contract** — publishes approved data products for analytics, applications, ML, and AI.

## Stakeholders

| Stakeholder | Need | Platform response |
|---|---|---|
| Data producer | Simple, documented onboarding | Adapter template and versioned contract |
| Data engineer | Reliable replay and standardized processing | Kinesis retention, Bronze history, idempotent transformations |
| Analyst | Consistent, discoverable metrics | Silver/Gold definitions, catalog, quality evidence |
| Security and compliance | Least privilege and auditable access | IAM, KMS, Lake Formation, CloudTrail, classification |
| Platform/SRE | Observable and recoverable services | SLOs, alarms, DLQs, runbooks, failure tests |
| ML/AI team | Trusted and authorized training/context data | Governed Gold products and explicit AI approval gate |
| Finance/FinOps | Predictable cost and ownership | Tags, budgets, unit-cost measures, lifecycle policies |

## Locked proving use case

The first source is the Coinbase Advanced Trade public WebSocket at `wss://advanced-trade-ws.coinbase.com`.

- `market_trades` supplies the business events.
- `heartbeats` proves connection health and drives operational metrics.
- `BTC-USD` and `ETH-USD` are the initial product allowlist.
- One Coinbase `market_trades` message remains one raw transport record through Bronze; Silver later explodes it into individual trade rows.
- `product_id` defines the per-instrument Kinesis ordering domain.
- Coinbase REST recovery is best-effort; Phase 1 does not claim source-side historical replay.

This workload proves sustained connectivity, ordering, burst traffic, schema handling, deduplication, gap reporting, Kinesis replay, and time-window analytics. It is a proving workload—not a limitation of the platform.

## Proposed business outcomes

These are target outcomes to validate; they are not claimed as achieved until evidence is committed.

| Outcome | Proposed measure |
|---|---|
| Faster source onboarding | A second source uses the adapter and contract without redesigning downstream services |
| Explainable reliability | Every accepted event is delivered, quarantined, or present in a retry path |
| Trusted analytics | Source-to-Bronze reconciliation and Silver quality checks are reproducible |
| Controlled access | Each role can access only the approved zone and columns |
| Safe reprocessing | Bronze can recreate Silver and Gold after a rule change |
| Cost transparency | Monthly and per-million-event costs are estimated and measured |
| AI readiness | Only approved Silver/Gold datasets can enter ML/AI workflows |

## Scope

### Phase 1 in scope

- one Coinbase Advanced Trade `market_trades` source adapter on ECS Fargate;
- raw source transport contract and target Silver schema policy;
- Kinesis Data Streams as the real-time backbone;
- unparseable-transport quarantine and exhausted-delivery DLQ;
- DynamoDB for checkpoints, idempotency, and control state—not as the default event queue;
- Terraform, CI/CD, IAM, KMS, Secrets Manager, CloudWatch, CloudTrail, tagging, and budgets;
- failure tests, runbook, evidence, and an architecture approval gate.

### Deferred

- Bronze/Silver/Gold implementation;
- enterprise multi-account landing zone;
- production BI dashboards;
- ML model training and generative-AI features;
- active/active multi-region architecture.

## Non-goals

- inventing a universal schema for every business domain;
- guaranteeing end-to-end exactly-once delivery;
- using every AWS analytics service;
- presenting reference patterns as completed production outcomes;
- storing credentials, personal data, or unapproved datasets in Git.
