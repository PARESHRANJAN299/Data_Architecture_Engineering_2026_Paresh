# Build plan — AWS-native

1. S3 data-lake zones and IAM/Lake Formation access model.
2. Kinesis + Firehose streaming ingest into Bronze.
3. Glue Catalog, schema/partition strategy, and Bronze-to-Silver Spark transformation.
4. EventBridge orchestration, retries, error prefix, and replay procedure.
5. Silver-to-Gold aggregations and Athena/Redshift serving.
6. Data quality, CloudWatch monitoring, Macie classification, and cost controls.
7. End-to-end load, duplicate, late-event, failure, and recovery tests.
