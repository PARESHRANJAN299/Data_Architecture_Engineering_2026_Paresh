# ECS, ECR and Fargate Interview Guide

**Owner:** Paresh Ranjan Rout

**Audience:** Data Engineer and Data Architect

**Practice standard:** Beginner, Medium and Company-scale Scenario

> Company names describe interview-style scale and business context only. They do not claim those companies use this exact architecture.

## How expectations differ by role

| Data Engineer | Data Architect |
|---|---|
| Build, configure, deploy, monitor and troubleshoot the workload | Select the runtime, define boundaries, govern risk and defend trade-offs |
| Explain image, task, logs, retries and failures | Explain reliability, security, scale, cost and operating model |
| Produce implementation and test evidence | Define measurable acceptance gates and target-state evolution |

## Answer framework

For every ECS/Fargate design question, answer in this order:

1. State whether the question concerns application packaging, runtime management or business-data movement.
2. Identify the image, task definition, service and Fargate compute responsibilities.
3. Separate task-role permissions from execution-role permissions.
4. Explain network placement and external/AWS service connectivity.
5. Define desired count, health, restart and deployment behavior.
6. Address logs, metrics, alerts and troubleshooting evidence.
7. Cover image security, versioning, rollback and lifecycle.
8. Compare reliability, control and cost with EC2, Lambda or another runtime.

## Mode 1 — Beginner

### Data Engineer questions

#### 1. What is a container image?

**Strong answer:** It is an immutable packaged application containing the runtime, libraries, source code and startup command. It is not a photograph, virtual server or running process.

#### 2. What does Amazon ECR store?

**Strong answer:** ECR stores Docker/OCI container images and compatible artifacts in repositories. It does not run the image or process Coinbase data.

#### 3. What is the difference between an image and a container?

**Strong answer:** The image is the stored package. A container is a running instance created from that image. Multiple containers can start from the same immutable image.

#### 4. Where does the Coinbase Python program run?

**Strong answer:** It runs inside a container on Fargate-managed compute. ECS defines and manages the task; ECR only stores the image used to start it.

### Data Architect questions

#### 5. What is the difference between ECS and Fargate?

**Strong answer:** ECS is the orchestration and service-management control plane. Fargate is the serverless container compute option that supplies CPU, memory and task networking without the team managing EC2 hosts.

#### 6. What does an ECS task definition describe?

**Strong answer:** It versions how a task should run: image, CPU, memory, ports, environment, logging, task role, execution role, health checks and other container settings.

#### 7. What does an ECS Service do?

**Strong answer:** It runs and maintains a specified number of task instances from a task definition. If a task stops or becomes unhealthy, the service scheduler attempts to replace it to maintain desired count.

#### 8. Why use two IAM roles?

**Strong answer:** The execution role belongs to the ECS/Fargate platform for image pull and logging. The task role belongs to application code for data-plane calls such as Kinesis writes. Separation reduces blast radius and clarifies audit ownership.

## Mode 2 — Medium

### Data Engineer questions

#### 1. A Fargate task cannot pull its ECR image. What do you check?

**Strong answer:** Check the image URI/tag or digest, execution role and `AmazonECSTaskExecutionRolePolicy`, ECR repository access, task subnet route or ECR VPC endpoints, security groups and ECS stopped-task reason. Do not change the application's Kinesis task role.

#### 2. Why prefer a version or image digest over `latest`?

**Strong answer:** A version/digest makes deployment reproducible and rollback deterministic. A mutable `latest` tag can point to different code over time and makes incident reconstruction difficult.

#### 3. Why enable ECR image scanning and tag immutability?

**Strong answer:** Scanning identifies known package vulnerabilities. Tag immutability prevents an existing release tag from being overwritten, protecting traceability between reviewed code, image digest and deployed task definition.

#### 4. Where should the adapter write logs?

**Strong answer:** Write structured logs to standard output/error. The ECS `awslogs` driver sends them to CloudWatch through the execution role. Include event type, product, sequence, retry count and error category without leaking payloads or credentials.

### Data Architect questions

#### 5. Why choose Fargate instead of direct EC2 for this adapter?

**Strong answer:** Fargate removes host provisioning, patching and container-instance management, fitting a small long-running adapter. EC2 can reduce unit cost at sustained scale and gives host-level control, but transfers more operational responsibility to the team.

#### 6. Why not use Lambda for the continuous Coinbase WebSocket?

**Strong answer:** The adapter maintains a long-lived outbound connection and continuous in-memory health state. Lambda is optimized for bounded event-driven invocations and has an execution-duration limit; ECS/Fargate is a more natural fit for a persistent process.

#### 7. Does `desired count = 1` provide high availability?

**Strong answer:** It provides automatic replacement, not uninterrupted high availability. There can be a restart/reconnect gap. Multiple tasks may improve availability but introduce duplicate subscriptions, ordering, idempotency and source-limit questions that must be designed.

#### 8. How do you control ECR storage growth?

**Strong answer:** Use lifecycle policies to expire unneeded images after protecting active releases and rollback versions. Preview lifecycle effects, retain traceable digests and apply equivalent policies in every replicated Region/account.

## Mode 3 — Company-scale scenarios

### Data Engineer scenarios

#### 1. The container starts and exits every thirty seconds

**Question:** ECS keeps replacing it. How do you diagnose the restart loop?

**Strong answer direction:** Inspect stopped-task reason, container exit code and CloudWatch startup logs; run the same image with equivalent configuration; validate the command, environment, network access and health check. Do not treat repeated replacement as successful availability.

#### 2. Coinbase records are duplicated after task replacement

**Question:** What should the pipeline do?

**Strong answer direction:** Treat transport as at-least-once, preserve a deterministic source/event identity, make downstream processing idempotent, record reconnect boundaries and reconcile accepted/acknowledged/retried counts. ECS replacement cannot provide exactly-once business outcomes.

#### 3. A new image version produces no CloudWatch logs

**Question:** Is this a task-role or execution-role issue?

**Strong answer direction:** Start with execution role, log configuration, log group/Region and task networking. Also confirm the process starts and writes to stdout/stderr. The Kinesis task role does not authorize the `awslogs` driver.

#### 4. A deployment introduces a bad adapter version

**Question:** How do you recover safely?

**Strong answer direction:** Stop promotion, identify the last known-good image digest and task-definition revision, roll the ECS service back, monitor reconnect/gap metrics and reconcile affected records. Preserve immutable image/version evidence for the incident.

### Data Architect scenarios

#### 5. Netflix-like global launch surge

**Question:** Should one adapter task automatically scale to ten tasks?

**Strong answer direction:** First analyze whether multiple Coinbase connections/subscriptions are permitted and whether they cause duplicates. Scaling the adapter is different from scaling Kinesis consumers. Define partition ownership, leader election or source sharding before increasing desired count.

#### 6. LinkedIn-like zero-downtime deployment

**Question:** How would you update the adapter without creating a message gap or double subscription?

**Strong answer direction:** Define rolling or blue/green behavior, health/readiness gates, connection handoff, duplicate suppression and rollback. A persistent external WebSocket may require controlled overlap plus idempotency or explicit single-active ownership.

#### 7. Walmart-like development and production separation

**Question:** How do you prevent a development image or task from writing to production streams?

**Strong answer direction:** Use separate AWS accounts where possible, environment-specific ECR repositories/task roles, exact resource ARNs, immutable promotion, SCPs/permission boundaries and deployment gates that verify image digest and task-definition inputs.

#### 8. Databricks-like cross-account platform

**Question:** A central platform account builds images, but workload accounts run them. What must the architecture address?

**Strong answer direction:** Define ECR cross-account repository policy and authorization, immutable digests, scanning/signing/provenance, regional replication, execution-role permissions and controlled promotion. Keep application task roles owned by workload accounts and scoped to their data resources.

## Fast interview comparisons

| Question | Best short answer |
|---|---|
| ECR vs ECS | ECR stores images; ECS manages running tasks |
| ECS vs Fargate | ECS orchestrates; Fargate supplies managed compute |
| Image vs container | Stored package vs running instance |
| Task vs Service | One task instance vs manager maintaining desired task count |
| Task role vs execution role | Application AWS access vs ECS platform operations |
| EC2 vs Fargate | Team-managed hosts/control vs managed container compute/simplicity |
| Replacement vs high availability | Restart capability vs uninterrupted service design |
| Policy simulation vs runtime proof | Static authorization evaluation vs real deployment evidence |

## Portfolio-ready evidence expected

### Data Engineer evidence

- Reproducible image build and immutable digest.
- ECR vulnerability-scan result and lifecycle policy preview.
- Task-definition revision with roles, CPU, memory and logging.
- Successful image pull and CloudWatch startup logs.
- Health/restart test and stopped-task diagnosis.
- Coinbase-to-Kinesis count reconciliation.

### Data Architect evidence

- Runtime decision and alternatives with cost/control triggers.
- RTO/RPO and desired-count rationale.
- Multi-AZ, task-replacement and source-gap analysis.
- IAM, network and image-supply-chain boundaries.
- Deployment/rollback strategy.
- Scaling model that addresses duplicate subscriptions and ordering.

## AWS references

- [Amazon ECR private repositories](https://docs.aws.amazon.com/AmazonECR/latest/userguide/Repositories.html)
- [Create an ECR repository and configure tag immutability](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-create.html)
- [Amazon ECR lifecycle policies](https://docs.aws.amazon.com/AmazonECR/latest/userguide/LifecyclePolicies.html)
- [Amazon ECS services](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html)
- [Amazon ECS service desired count](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service_definition_parameters.html)
- [Amazon ECS task execution role](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html)
