# DynamoDB Table Design — Durable Interaction Staging

Implements the outbox pattern confirmed in the whiteboard review: the application writes here first, durably, before anything touches Kinesis.

---

## Table: `chat_interactions_staging`

| Attribute | Type | Role |
|---|---|---|
| `interaction_id` | String | **Partition key** |
| `ingest_timestamp` | String (ISO 8601) | **Sort key** |
| `session_id` | String | |
| `user_id` | String | tokenized value only, never raw |
| `payload` | Map (JSON) | the interaction body, PII-scanned and masked before this record is written |
| `payload_hash` | String | SHA-256, dedup key |
| `processing_status` | String | `PENDING` \| `PROCESSING` \| `SENT` \| `FAILED` |
| `retry_count` | Number | incremented on each failed Fargate push attempt |
| `last_attempt_at` | String | for backoff logic |

## Required Global Secondary Index

**GSI name:** `status-ingest-index`
**Partition key:** `processing_status`
**Sort key:** `ingest_timestamp`

**Why this index is mandatory, not optional:** without it, the Fargate poller's only way to find pending records is a full table scan on every poll cycle. That's fine at 100 records. At the backlog sizes discussed in the capacity conversation (144M records/hour if the gap is sustained), a scan becomes slow and expensive fast. The GSI makes "give me the oldest 500 PENDING records" a cheap, direct query.

## Fargate poller query pattern

```
Query on GSI status-ingest-index
WHERE processing_status = "PENDING"
ORDER BY ingest_timestamp ASC
LIMIT 500
```

Oldest-first ordering matters — otherwise new records could be pushed to Kinesis while old ones starve at the back of an unordered pile.

## State transitions

```
PENDING  --Fargate picks it up-->  PROCESSING
PROCESSING  --Kinesis PutRecord succeeds-->  SENT
PROCESSING  --Kinesis PutRecord fails-->  PENDING  (retry_count += 1)
PENDING  --retry_count exceeds threshold-->  FAILED  (routed to a dead-letter review, not silently dropped)
```

**Why a `PROCESSING` state exists, not just `PENDING`/`SENT`:** if Fargate crashes mid-push, a record stuck at `PENDING` forever would never be distinguished from one nobody has tried yet. `PROCESSING` plus a timestamp lets a recovery job detect "this has been PROCESSING for 10 minutes with no update" and safely reset it to `PENDING` for retry.

## Capacity mode

**On-demand**, not provisioned. Traffic here is inherently bursty (tied to chat usage patterns), and on-demand avoids having to pre-guess a write capacity number — same reasoning that applies to Kinesis on-demand mode, just for the table instead of the stream.

## What this table is NOT for

It is not a permanent store. Once a record reaches `SENT`, it has done its job. A TTL attribute (`expire_at`, set to e.g. 7 days after `ingest_timestamp`) should be added so old `SENT` records age out automatically — the real historical copy lives in S3 Bronze once it's through Kinesis and Firehose, not here.
