# AWS Cloud - June 20 to June 30 - 10 days - 4 hours daily - Paresh keep hardwork 💪

## ✅ Roadmap Status: Complete

Full topic list from the roadmap — **S3, IAM, Glue, EMR, Redshift, Athena, Lambda, Kinesis basics, and how they connect to Databricks** — all covered.

---

## S3

- Object storage fundamentals — immutable objects, no in-place append/edit
- Four bucket types: **General purpose** (default, any file), **Directory** (low-latency, single-zone, ML/AI), **Table** (native Iceberg, lakehouse pipelines), **Vector** (embeddings, AI semantic search)
- Diagram: `s3_bucket_types_comparison.svg`

## IAM

- Users, Groups, Policies, Roles — how each relates
- Groups = permanent access for people; Roles = temporary, borrowed access for services (Lambda, Glue) or anything that isn't a logged-in human
- Inline policy (tied to one entity, deleted with it) vs Customer-managed policy (standalone, reusable across many entities)
- Multiple services each assuming their **own** dedicated role — never a shared role
- Diagrams: `iam_policy_group_role_relationship.svg`, `multiple_services_assuming_roles.svg`

## Lambda

- Serverless compute, event-driven — S3 upload triggers, EventBridge Scheduler for cron-style jobs
- Lambda ≠ its own trigger — always needs a separate wake-up mechanism
- 15-minute execution limit — why heavy transform work goes to Glue instead
- Debugged a real S3 → Lambda trigger end-to-end via CloudWatch Log groups (`/aws/lambda/...`), confirmed successful invocation from raw event payload
- **Project built:** Content-hash (SHA-256) deduplication architecture — S3 → Lambda → DynamoDB hash lookup → clean/quarantine routing. See `Project- Content-Hash Deduplication Pipeline for File Uploads.docx`

## Glue

- Serverless data integration — ETL jobs, Data Catalog, Crawlers, Job Bookmarks (incremental processing, Glue's version of Auto Loader)
- Standard vs Flex execution class — same serverless model either way, Flex trades startup-time guarantee for ~35% lower cost
- No classic/persistent compute option at all (unlike Databricks) — that need is served by EMR instead
- Catalog → Database → Table hierarchy (AWS's equivalent of Databricks' Catalog → Schema → Table, one level shifted)

## Athena

- Serverless SQL query engine on S3 data, no infrastructure, pay-per-data-scanned
- Query result location requirement — customer-managed S3 bucket vs Athena-managed results
- **CTAS** (Create Table As Select) — one command doing filter + physical write + table registration together
- **External table** (pointer only, DROP leaves S3 data untouched) vs **Managed/Iceberg table** (Athena owns the data, DROP deletes it too) — confirmed down to the actual `data/` and `metadata/` folder structure on S3
- Diagram: `ctas_external_vs_managed_table.svg`

## EMR

- Managed, persistent Spark/Hadoop clusters — AWS's classic-compute answer, same underlying EC2 as Databricks classic compute
- EMR on EC2 / EMR Serverless / EMR on EKS
- Master, core, and task node architecture; EMRFS for reading/writing S3 directly

## RDS & Redshift

- RDS = row-based storage, OLTP, single-record transactions
- Redshift = column-based storage, OLAP, MPP architecture, built for heavy aggregation across millions of rows
- Redshift Spectrum can query S3 directly, same as Athena — the real difference is ad-hoc pay-per-query (Athena) vs dedicated/repeated BI workloads (Redshift)
- Diagram: `row_vs_column_storage.png`

## Kinesis

- Three services: **Data Streams** (the belt — captures and holds the live feed, multiple independent consumers), **Amazon Data Firehose** (auto-batches and delivers to S3/Redshift, no code), **Managed Service for Apache Flink**, formerly Kinesis Data Analytics (real-time processing directly on the stream)
- Designed a real pipeline: millisecond stock data → Kinesis Data Streams → two parallel consumers (Firehose → S3 raw, Lambda → structured write into RDS)
- Diagram: `stock_data_streaming_pipeline_aws.svg`

## Governance layer (Lake Formation & Macie)

- **IAM** = resource-level access (whole table/bucket, on or off)
- **Lake Formation** = row/column-level filtering on top of the Glue Data Catalog — hides restricted columns/rows entirely (not the same as true data masking)
- **Macie** = sensitive-data discovery only — scans S3, flags PII/security risks, does not control access itself
- Diagram: `iam_vs_lakeformation.png`

## Full pipeline design

- Complete Unilever Bronze → Silver → Gold medallion architecture mapped to real AWS services, roles per service, and IAM groups per team (DE, AI, BI)
- Diagram: `unilever_medallion_pipeline_groups_roles.svg`

## Capstone project

- **AI Chatbot Data Platform** — production-scale design combining AWS + Databricks, four teams (Data Engineering, AI/ML, Insights, Data Analytics), real open dataset (LMSYS-Chat-1M) as the source. See `10_Projects_Portfolio/AI_Chatbot_Data_Platform/`
