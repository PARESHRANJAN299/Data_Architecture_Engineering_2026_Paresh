# Canonical Event Schema — Chat Interaction (Phase 1, Entry 2)

**Source locked:** Chat interaction data
**Status:** Design complete, infrastructure not yet built

---

## Why this doesn't require a new schema design

The multi-source canonical envelope was already designed before this source was picked. A chat interaction is just a *different payload* inside the *same envelope* — this is the actual proof that the envelope pattern works, not a coincidence.

| Envelope field | Value for a chat interaction |
|---|---|
| `event_id` | `interaction_id` |
| `event_type` | `"chat_interaction"` |
| `event_source` | `"chatbot_app"` (or the specific application name) |
| `event_timestamp` | `question_timestamp` — when the user actually asked |
| `ingest_timestamp` | when the DynamoDB record is created |
| `schema_version` | `"v1"` |
| `producer_id` | the specific application/service instance |
| `user_id` | masked/tokenized at write time (see below) |
| `session_id` | groups multiple interactions in one conversation |
| `device_id` | null — not applicable to this source |
| `geo_country` | optional, if available from the request |
| `payload` | see below — the interaction-specific fields |
| `payload_hash` | SHA-256 of the payload, same dedup mechanism as every other source |
| `is_pii` | `true` — `user_question` / `generated_answer` may contain PII |
| `processing_status` | `PENDING` / `PROCESSING` / `SENT` / `FAILED` |

## The `payload` — interaction-specific fields

```json
{
  "user_question": "What is XYZ?",
  "generated_answer": "XYZ means...",
  "answer_timestamp": "2026-08-10T10:30:05Z",
  "channel": "web",
  "model": "gpt-4o"
}
```

## Full example record

```json
{
  "event_id": "5001",
  "event_type": "chat_interaction",
  "event_source": "chatbot_app",
  "event_timestamp": "2026-08-10T10:30:01Z",
  "ingest_timestamp": "2026-08-10T10:30:01.400Z",
  "schema_version": "v1",
  "producer_id": "chatbot-web-prod",
  "user_id": "tok_9f2c3a...",
  "session_id": "ABC",
  "device_id": null,
  "geo_country": "IN",
  "payload": {
    "user_question": "What is XYZ?",
    "generated_answer": "XYZ means...",
    "answer_timestamp": "2026-08-10T10:30:05Z",
    "channel": "web",
    "model": "gpt-4o"
  },
  "payload_hash": "9f2c...",
  "is_pii": true,
  "processing_status": "PENDING"
}
```

## Masking scope for this source (applies ADR-001 — mask on write)

| Field | Treatment | Why |
|---|---|---|
| `user_id` | **Tokenized** (reversible, KMS-held key) | Needed to group a user's interactions later; must remain linkable, so masking (irreversible) is wrong here — tokenization is correct |
| `user_question` / `generated_answer` | **Scanned for embedded PII** (emails, phone numbers) and masked in place if found | Free-text fields can leak PII a user typed voluntarily |
| `session_id` | Left as-is | Not personally identifying on its own |

**Note on tokenize vs mask, since ADR-001 uses "mask" loosely:** `user_id` needs to be tokenized, not masked — the platform needs to know "these 12 interactions are the same user" without knowing *who* that user is. A one-way mask would break that grouping entirely. Free-text PII inside the question/answer, by contrast, has no legitimate downstream need to be reversed — full masking is correct there.
