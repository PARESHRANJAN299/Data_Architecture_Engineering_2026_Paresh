# Phase 1 — ECS/Fargate Deployment Evidence

**Status: ✅ DEPLOYED AND VERIFIED**

This checkpoint proves that the Python Coinbase adapter is running continuously on AWS Fargate, managed by an Amazon ECS service, and writing live Coinbase messages to Amazon Kinesis Data Streams.

![Phase 1 deployment evidence](../architecture/phase-1-deployment-evidence-snapshot.svg)

## What we built, in simple language

1. **ECR stores the packaged application.** The approved `phase1-v2` Docker image contains Python, required libraries and the Coinbase adapter code.
2. **The task definition is the instruction sheet.** It tells ECS which image, CPU, memory, roles, command and CloudWatch log group to use.
3. **Fargate provides the computer.** It supplies CPU and memory and starts a container from the ECR image.
4. **The ECS service keeps one task running.** Desired count is `1`; if the task stops, ECS starts a replacement.
5. **The Python adapter performs the work.** It connects to Coinbase WebSocket, receives live JSON and calls Kinesis `PutRecord`.
6. **The task role grants the application permission.** It allows only `PutRecord` and `PutRecords` on the selected Kinesis stream.
7. **The execution role supports startup.** It allows the ECS runtime to pull the image from ECR and deliver container logs to CloudWatch.
8. **CloudWatch shows runtime evidence.** The logs contain `coinbase_connecting` and `coinbase_subscribed`.
9. **Kinesis metrics show real writes.** `PutRecord` activity is non-zero, success is `1`, and observed average latency is approximately `4.3 ms`.

## Verified AWS resources

| Component | Configuration | Evidence |
|---|---|---|
| Kinesis stream | `lca-coinbase-market-trades-dev`; provisioned; one shard; one-day retention; KMS encryption | Active; manual record test passed; live `PutRecord` metrics visible |
| ECS application task role | `lca-coinbase-ecs-task-role-dev` | Policy Simulator allowed `PutRecord` and `PutRecords` for the exact stream ARN |
| ECS task execution role | `lca-coinbase-ecs-execution-role-dev` | `AmazonECSTaskExecutionRolePolicy` attached |
| ECR repository | `lca-coinbase-adapter-dev` | Private repository created with immutable tags, KMS encryption and scan-on-push |
| Approved image | `phase1-v2` | Digest `sha256:e750284e083dd850564f231b0d0a6f850d9db6f5f3b7b5830cfd0820f0ac0e46`; scan completed with zero findings |
| CloudWatch log group | `/ecs/lca-coinbase-adapter-task-dev` | Standard log class; seven-day retention |
| ECS task definition | `lca-coinbase-adapter-task-dev:1` | Active; Fargate; Linux/X86_64; `awsvpc`; 0.25 vCPU; 0.5 GiB |
| ECS cluster | `lca-coinbase-streaming-cluster-dev` | Active; Fargate-only cluster |
| ECS service | `lca-coinbase-adapter-task-dev-service-jh943f9h` | Active; one desired, one running, zero pending; deployment successful |

## Exact container setup

```text
Container name: coinbase-adapter
Essential: yes
Image: ECR phase1-v2 pinned by SHA256 digest
Port mapping: none required
Persistent volume: none required
CPU: 0.25 vCPU
Memory: 0.5 GiB
Command:
python,-m,coinbase_adapter.main,--kinesis-stream,lca-coinbase-market-trades-dev
```

No inbound port is required because the adapter opens outbound connections to Coinbase and Kinesis. The application does not host an HTTP website or API.

## Why three IAM roles appeared

| Role | Who uses it? | Simple purpose |
|---|---|---|
| Task role | Python application inside the container | Permission to write records to the selected Kinesis stream |
| Task execution role | ECS/Fargate runtime during startup | Pull the ECR image and send stdout/stderr logs to CloudWatch |
| `AWSServiceRoleForECS` | ECS control plane | Manage ECS-owned resources such as tasks, services and networking on our behalf |

The first cluster creation attempt showed **Unable to assume the service linked role**. We verified that `AWSServiceRoleForECS` already existed, trusted `ecs.amazonaws.com`, and had `AmazonECSServiceRolePolicy` attached. Retrying the cluster creation then succeeded.

## Docker image security gate

| Version | Result | Decision |
|---|---|---|
| `phase1-v1` | 4 critical, 8 high and 6 medium findings | Rejected |
| `phase1-v2` | Scan `COMPLETE`; empty severity counts | Approved for this development checkpoint |

`phase1-v2` uses the Alpine-based Python image and passed the local Coinbase one-message test before it was pushed to ECR.

## How we know real data is moving

```text
CloudWatch application logs
  coinbase_connecting
  coinbase_subscribed

Kinesis metrics
  PutRecord activity       > 0
  PutRecord.Success        = 1
  PutRecord average latency ≈ 4.3 ms
```

`PutRecords` can remain empty because the current adapter calls the singular `PutRecord` API once per raw Coinbase message.

## Current boundary

```text
Coinbase WebSocket
        ↓ VERIFIED
Python adapter on ECS/Fargate
        ↓ VERIFIED
Kinesis Data Streams
        ↓ NEXT
Amazon Data Firehose
        ↓ NEXT
S3 Bronze
```

The Coinbase-to-Kinesis runtime is verified. **Amazon Data Firehose and S3 Bronze are not yet created**, so the full Phase 1 source-to-Bronze path is still in progress.

