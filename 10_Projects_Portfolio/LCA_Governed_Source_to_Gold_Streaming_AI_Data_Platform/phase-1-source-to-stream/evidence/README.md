# Phase 1 Evidence

Evidence files record reproducible test summaries without committing live Coinbase payloads, credentials, or sensitive logs.

| Evidence | Scope |
|---|---|
| [`local-adapter-step-3-4.json`](local-adapter-step-3-4.json) | Unit/contract tests, bounded live connectivity and container smoke test |
| [`local-kinesis-sink-test.json`](local-kinesis-sink-test.json) | Stubbed `PutRecord` contract, unchanged UTF-8 payload, exact stream target and full local regression suite |
| [`manual-kinesis-write-read-smoke-test.json`](manual-kinesis-write-read-smoke-test.json) | User-performed CloudShell `PutRecord`, KMS response and Data Viewer readback from `Trim horizon` |

The Kinesis sink evidence is a local unit-test result. The separate manual smoke test proves that the AWS stream accepts and returns a test record, but it does not prove that the Python sink or ECS task role works. Application delivery evidence begins only after ECR packaging and ECS/Fargate deployment.

Live JSONL files remain temporary and are excluded by `.gitignore`. The committed SHA-256 value provides a reference for the bounded capture used during the test session; it is not presented as durable source replay evidence.
