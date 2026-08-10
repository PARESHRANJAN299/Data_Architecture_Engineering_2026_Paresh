# Technology Decisions, Alternatives, Pros and Cons

The selections below are the architecture baseline. Each remains subject to proof, cost measurement, and an ADR revisit trigger.

## Source runtime

| Option | Strengths | Limitations | Decision |
|---|---|---|---|
| ECS Fargate | Fits long-running WebSockets, container portability, task IAM role, managed host layer | Minimum running cost, container operations, scaling is not event-native | **Selected for Phase 1** |
| AWS Lambda | Simple operations and event scaling | Execution duration and connection lifecycle make persistent WebSockets awkward | Use for bounded control tasks only |
| EC2 | Maximum network/runtime control | Patching, capacity, and host operations | Revisit only for specialized performance or cost |
| EKS | Rich platform and portability | Excessive platform overhead for the first adapter | Revisit when Kubernetes is an organizational standard |

## Streaming backbone

| Option | Strengths | Limitations | Decision |
|---|---|---|---|
| Kinesis Data Streams | Managed AWS stream, partition ordering, retention/replay, multiple consumers | AWS-specific API, partition-key discipline, retention cost | **Selected** |
| Amazon MSK | Kafka ecosystem, portability, broad connectors | Higher operating complexity and baseline cost | Revisit for Kafka standardization or connector demand |
| SQS | Durable worker queue, DLQ/redrive, easy decoupling | Not a replayable multi-consumer event log | Selected only for failure/retry workflows |
| EventBridge | Routing and SaaS/AWS integration | Not the primary high-volume ordered event log | Use for control-plane events |

## Buffer and recovery

| Option | Strengths | Limitations | Decision |
|---|---|---|---|
| Direct producer retry to Kinesis | Lowest latency and least complexity | Retry state lives in adapter | Default happy path |
| SQS retry queue/DLQ | Purpose-built persistence, visibility, redrive | Adds another delivery hop | **Selected for exhausted delivery** |
| DynamoDB event buffer | Queryable state and conditional writes | Polling, write amplification, ordering, TTL and cleanup complexity | Not the default queue |
| S3 store-and-forward | Cheapest long retention and replay | Higher latency and object batching complexity | Use for quarantine and durable raw history |

## Schema technology

| Option | Strengths | Limitations | Decision |
|---|---|---|---|
| Glue Schema Registry | Native Kinesis integration; compatibility modes; Avro, JSON Schema, Protobuf | AWS coupling and language-integration considerations | **Selected** |
| JSON Schema in application only | Language-neutral and transparent | Governance and compatibility enforcement become custom | Keep canonical schema in Git as source |
| Confluent Schema Registry | Mature Kafka ecosystem | Additional platform and best fit with Kafka/MSK | Revisit if MSK becomes backbone |

## Bronze delivery

| Option | Strengths | Limitations | Decision |
|---|---|---|---|
| Amazon Data Firehose | Managed buffering, compression, partitioning, S3 delivery | Buffering latency and limited complex processing | **Phase 2 baseline** |
| Lambda consumer | Flexible transformation | Concurrency, retry, and payload constraints | Only for lightweight enrichment |
| Custom KCL consumer | Full control over checkpoint and batching | More code and operations | Revisit for special delivery semantics |

## Silver processing

| Option | Strengths | Limitations | Decision |
|---|---|---|---|
| AWS Glue/Spark | Scalable ETL, catalog integration, broad transformations | Startup latency and Spark tuning | **Default batch/micro-batch choice** |
| Managed Service for Apache Flink | Low-latency stateful event-time processing | Stateful streaming complexity | Use when latency/state requirements prove it |
| Lambda | Low operations for small transformations | Poor fit for heavy joins and large state | Use only for bounded operations |
| EMR Serverless | More runtime/version control | More platform choices to manage | Revisit for advanced Spark requirements |

## Table format

Apache Iceberg is the target Silver/Gold table format because it supports schema evolution, partition evolution, snapshots, time travel, and multiple compatible query engines. Plain Parquet remains the Bronze storage format where immutability and simplicity dominate.

## Query and serving

| Requirement | Preferred service | Why |
|---|---|---|
| Infrequent ad-hoc SQL on S3 | Athena | Serverless and pay-per-query |
| Repeated BI, concurrency, dimensional models | Redshift Serverless | Warehouse performance and workload management |
| Managed dashboarding | QuickSight | AWS-native governed BI integration |
| Operational low-latency lookup | DynamoDB/OpenSearch depending access pattern | Do not force analytical storage into an operational API |
| ML lifecycle | SageMaker | Training, registry, deployment, monitoring |
| Governed generative AI | Bedrock | Managed foundation-model access and AWS controls |

## Mandatory revisit triggers

- sustained throughput or cost exceeds the validated Kinesis operating envelope;
- source count or connector needs make Kafka/MSK materially simpler;
- latency target requires stateful processing before S3;
- regulatory requirements demand different retention, account isolation, or keys;
- team operating model changes the build-versus-managed-service balance;
- query concurrency or spend invalidates the Athena/Redshift split.
