# AI Chatbot Data Platform — AWS-native

An independent AWS-native implementation of the same chatbot data-platform problem. This project will use AWS services for ingestion, storage, processing, metadata, analytics, security, and operations.

## Planned architecture

`Chatbot events -> Kinesis -> S3 Bronze -> Glue / EMR processing -> S3 Silver and Gold -> Athena / Redshift -> analytics and AI consumers`

Core AWS services will include Kinesis, S3, EventBridge, Glue, Glue Data Catalog, Athena, Redshift, IAM, Lake Formation, CloudWatch, and Macie. The Glue crawler is optional metadata discovery; Glue jobs (or EMR/Spark) perform the actual transformations and writes.

Read [docs/aws-architecture.md](docs/aws-architecture.md) for the project boundary and [docs/build-plan.md](docs/build-plan.md) for the implementation sequence.

## Project status

Separate project scaffold created. The existing hybrid project remains unchanged and is kept as historical work/evidence; this folder will become the clean AWS-native portfolio implementation.
