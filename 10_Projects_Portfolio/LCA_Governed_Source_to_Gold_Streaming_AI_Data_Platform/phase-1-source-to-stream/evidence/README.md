# Phase 1 Evidence

Evidence files record reproducible test summaries without committing live Coinbase payloads, credentials, or sensitive logs.

| Evidence | Scope |
|---|---|
| [`local-adapter-step-3-4.json`](local-adapter-step-3-4.json) | Unit/contract tests, bounded live connectivity and container smoke test |

Live JSONL files remain temporary and are excluded by `.gitignore`. The committed SHA-256 value provides a reference for the bounded capture used during the test session; it is not presented as durable source replay evidence.
