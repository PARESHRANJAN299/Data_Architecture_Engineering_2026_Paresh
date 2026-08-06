# AWS-native architecture boundary

This project intentionally keeps the processing and governance AWS-native:

```mermaid
flowchart LR
  SRC["Chatbot application + APIs"] --> K["Kinesis Data Streams"]
  K --> F["Kinesis Data Firehose"]
  F --> B["Amazon S3 Bronze\nimmutable raw files"]
  B --> E["EventBridge"]
  E --> G["AWS Glue Spark jobs\nvalidate and transform"]
  G --> S["Amazon S3 Silver Delta/Iceberg/Parquet"]
  S --> GG["AWS Glue Spark jobs\naggregate"]
  GG --> GO["Amazon S3 Gold"]
  GO --> A["Athena"]
  GO --> R["Redshift"]
  C["Glue Data Catalog\nmetadata only"] -. tables and partitions .-> B
  C -. tables and partitions .-> S
  C -. tables and partitions .-> GO
  LF["IAM + Lake Formation + Macie + CloudWatch"] -. governs / monitors .-> B
  LF -. governs / monitors .-> S
  LF -. governs / monitors .-> GO
```

The AWS build will document exactly when a Glue crawler is useful and when jobs must update table metadata/partitions explicitly.
