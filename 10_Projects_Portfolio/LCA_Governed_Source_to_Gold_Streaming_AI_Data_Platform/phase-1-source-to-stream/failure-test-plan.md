# Phase 1 Failure-Test Plan

| Test | Injection | Expected behavior | Pass evidence |
|---|---|---|---|
| Source disconnect | Terminate network/session | Bounded backoff and reconnect; gap identified | Timeline and gap report |
| Stale heartbeat | Suppress or stop heartbeat processing | Connection is marked unhealthy and alarm fires | Heartbeat-age metric and alarm evidence |
| Coinbase sequence gap | Drop one source message in the test adapter | Gap is detected; best-effort REST recovery or explicit unrecovered-gap record | Gap report and recovery decision |
| Multi-trade message | Provide one message containing multiple trades | One unchanged Kinesis/Bronze source record is preserved; Silver later produces one row per trade | Raw-payload comparison and Silver count reconciliation |
| Task failure | Stop active ECS task | Service replaces task and restores ingestion | ECS events and recovery time |
| Unparseable transport payload | Supply malformed JSON or an unreadable envelope | Raw transport record is quarantined; healthy flow continues | Object, metric, and correlation ID |
| Silver business-field failure | Remove a required trade field or change its type | Bronze remains unchanged; rejected Silver row and reason are recorded | Quality report and rejected-row evidence |
| Kinesis partial failure | Stub failed record responses | Retry only failed records | Unit/integration report |
| Throttling | Constrain/test producer throughput | Backoff; alarm; no retry storm | Metrics and logs |
| Duplicate delivery | Replay identical `event_id` | Downstream idempotency preserves one result | Reconciliation result |
| Hot partition | Concentrate partition keys | Alarm and documented re-partition response | Shard/partition metrics |
| DLQ redrive | Force delivery exhaustion | Message is investigated and safely redriven | Redrive evidence |
| Secret leak | Commit test secret signature | CI blocks change | Security-job output |
| IaC drift | Change a controlled setting | Plan/check identifies drift | Plan evidence |

## Reconciliation equation

For a bounded test window:

```text
events_received
= events_accepted + events_rejected_before_acceptance

events_accepted
= events_acknowledged_by_kinesis + events_in_retry_or_dlq
```

Differences must be explainable by documented Coinbase batching/connection semantics, test-window boundaries, measured duplicates, or an explicit unrecoverable source gap. “Close enough” is not a pass criterion.
