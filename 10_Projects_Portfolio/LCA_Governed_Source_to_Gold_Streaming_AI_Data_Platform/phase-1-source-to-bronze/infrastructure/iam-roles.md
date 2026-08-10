# IAM Roles — Phase 1, Entry 2

Three separate roles, one per component, each scoped to only what that component touches. Same least-privilege pattern used throughout this project.

---

## 1. `Masking_Lambda_Role`

**Assumed by:** `lambda.amazonaws.com`

**Permissions needed:**
- `kms:Encrypt` on the tokenization key only — this Lambda tokenizes, it never decrypts
- `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` (standard Lambda logging)

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "kms:Encrypt",
    "Resource": "arn:aws:kms:us-east-1:939390173271:alias/interaction-tokenization-key"
  }]
}
```

**Deliberately excluded:** `kms:Decrypt`. This role only ever tokenizes on the way in — reversing a token is a separate, more sensitive operation that belongs to a different role, requested only when a legitimate downstream need exists.

---

## 2. `Interaction_DynamoDB_Write_Role`

**Assumed by:** whatever writes the governed record — either the application itself, or an intermediate Lambda

**Permissions needed:**
- `dynamodb:PutItem` on `chat_interactions_staging` only

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "dynamodb:PutItem",
    "Resource": "arn:aws:dynamodb:us-east-1:939390173271:table/chat_interactions_staging"
  }]
}
```

---

## 3. `Fargate_Poller_Role`

**Assumed by:** `ecs-tasks.amazonaws.com`

**Permissions needed:**
- `dynamodb:Query` on the table **and its GSI** — both must be listed, the GSI is a separate resource
- `dynamodb:UpdateItem` — to move records `PENDING` → `PROCESSING` → `SENT`
- `kinesis:PutRecord`, `kinesis:PutRecords` on the target stream only

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["dynamodb:Query", "dynamodb:UpdateItem"],
      "Resource": [
        "arn:aws:dynamodb:us-east-1:939390173271:table/chat_interactions_staging",
        "arn:aws:dynamodb:us-east-1:939390173271:table/chat_interactions_staging/index/status-ingest-index"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["kinesis:PutRecord", "kinesis:PutRecords"],
      "Resource": "arn:aws:kinesis:us-east-1:939390173271:stream/chat-interactions-stream"
    }
  ]
}
```

**Why the GSI ARN is listed separately, not implied:** IAM does not treat an index as automatically covered by permission on its base table. A role with `Query` on the table but not the index ARN will fail with `AccessDeniedException` the moment it tries to query `status-ingest-index` — this is a common first-time mistake worth avoiding up front.

---

## Trust policy pattern (same for all three)

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "<service>.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
```

Replace `<service>` with `lambda`, or `ecs-tasks` as appropriate per role above.
