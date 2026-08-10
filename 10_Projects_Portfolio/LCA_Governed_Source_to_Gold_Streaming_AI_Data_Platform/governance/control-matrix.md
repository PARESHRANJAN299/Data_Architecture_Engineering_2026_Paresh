# AWS Governance and Control Matrix

| Control objective | Preventive control | Detective control | Evidence | Phase |
|---|---|---|---|---|
| No credentials in code | Task roles, Secrets Manager, protected branches | Secret scanning and CloudTrail review | CI result, secret inventory | 1 |
| Least-privilege runtime | Dedicated IAM producer role and scoped resource policies | Access Analyzer and denied-action alarms | Reviewed policy and access test | 1 |
| Encrypted data | TLS and KMS-encrypted Kinesis, SQS, DynamoDB, S3 | Config/security findings | Key policy and configuration export | 1 |
| Valid contracts | Glue Schema Registry compatibility policy | Rejection/quarantine metrics | Contract-test report | 1 |
| Approved external source | Versioned Coinbase source contract and allowlisted channels/products | Endpoint/schema/rate-limit review before release | ADR-004 and source-review record | 1 |
| Source-gap accountability | Sequence tracking, bounded reconnect and explicit recovery policy | Heartbeat-age and sequence-gap alarms | Gap report and reconciliation evidence | 1 |
| Accountable events | Stable identity, structured outcomes | Reconciliation and missing-state alarm | Reconciliation report | 1–2 |
| Controlled raw data | Private S3, block public access, restricted role | CloudTrail data events where justified | Bucket policy and access test | 2 |
| Retention compliance | Lifecycle and object-lock policy where required | Expiration and policy drift checks | Retention configuration | 2 |
| Trusted Silver data | Automated quality and deduplication rules | Quality score and failed-row trends | Quality report | 2 |
| Governed consumption | Lake Formation grants/LF-tags and approved Gold contracts | Access logs and periodic recertification | Access matrix and review | 3 |
| Safe AI use | Approved Gold datasets, bounded tools, evaluation gate | Prompt/output monitoring and evaluation | Model/data approval package | 3 |
| Cost accountability | Required tags, budgets, capacity limits | Cost anomaly and utilization alarms | Monthly unit-cost report | 1–3 |
| Recoverability | IaC, backups/retention, documented redrive | Scheduled recovery exercises | Recovery-test report | 1–3 |

## Separation of duties

- Deployment roles cannot grant themselves unrestricted data access.
- Data lake administrators manage permissions but do not automatically receive business-data access.
- Production apply requires an approved plan and protected environment.
- Emergency access is time-bound, logged, and reviewed.
- AI consumers cannot access Bronze by default.
