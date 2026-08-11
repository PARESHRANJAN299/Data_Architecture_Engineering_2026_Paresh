# ECS, ECR and Fargate — Simple Project Explainer

**Owner:** Paresh Ranjan Rout

**Purpose:** Explain where the Coinbase Python program runs and how AWS keeps it running, without mixing the application-deployment flow with the data flow.

## Start with one simple truth

Our Python program performs only this job:

```text
Connect to Coinbase
    ↓
Receive one live JSON message
    ↓
Send the same message to Kinesis
    ↓
Wait for the next message
```

The word **adapter** simply means **bridge**:

```text
Coinbase ← Python bridge → Kinesis
```

The program needs a computer that stays available. During development that computer can be a laptop. In AWS, our architecture uses Fargate-managed compute.

## The source of the confusion: two different flows

### Flow 1 — Deploy and start the application

This flow answers: **How does Python start running in AWS?**

```text
Python code
    ↓ packaged as a container image
Docker/OCI image
    ↓ stored
Amazon ECR
    ↓ selected and managed
Amazon ECS
    ↓ compute supplied
AWS Fargate
    ↓
Python program is running
```

### Flow 2 — Move the business data

This flow starts only after Python is running:

```text
Coinbase WebSocket
    ↓
Python adapter running on Fargate
    ↓
Kinesis Data Stream
    ↓ later
Firehose → S3 Bronze → Glue/Spark → Silver Iceberg
```

ECR and ECS do not transform Coinbase data. They belong to the application-deployment flow.

## What is the Python adapter?

Conceptually, it performs this loop:

```python
while True:
    message = receive_from_coinbase()
    send_unchanged_message_to_kinesis(message)
```

The real implementation also needs heartbeat checks, reconnect backoff, sequence-gap diagnostics, batching, retry handling and reconciliation. Those controls make the simple bridge reliable.

## Why does Docker appear?

Docker is not a new data service. It is a packaging method.

```text
Dockerfile = packaging recipe
Image      = sealed application package
Container  = running copy of that package
```

The image contains:

```text
small Linux runtime
+ Python
+ required libraries
+ Coinbase adapter source code
+ command that starts the adapter
```

It does not contain live Coinbase data, Kinesis records or AWS passwords.

## What is ECR?

**Amazon Elastic Container Registry is managed storage for container images. It is not a virtual server.**

```text
ECR repository: lca-coinbase-adapter

Possible versions:
    lca-coinbase-adapter:v1
    lca-coinbase-adapter:v2
    lca-coinbase-adapter:v3
```

ECR cannot run Python and does not connect Coinbase to Kinesis. When a task starts, Fargate downloads the selected image from ECR through AWS APIs.

## What is ECS?

**Amazon Elastic Container Service is the container manager.** It defines and supervises:

- which image version to run;
- CPU and memory;
- task and execution roles;
- VPC, subnets and security groups;
- environment configuration;
- CloudWatch logging;
- desired number of running tasks;
- deployment and replacement behavior.

ECS is the manager, not the hidden computer.

## What is Fargate?

**AWS Fargate supplies managed CPU, memory and networking for the task.** Python runs inside a container on that managed compute. We do not create, log in to, patch or maintain an EC2 server for it.

```text
Python adapter = worker
Fargate        = managed computer/workplace
ECS            = manager supervising the worker
ECR            = warehouse storing the worker's packaged software
```

## What happens when the task starts?

```text
1. ECS reads the task definition.
2. ECS asks Fargate to launch a task.
3. Fargate receives networking in a selected subnet.
4. The execution role authorizes the ECR image pull.
5. Fargate downloads the image from ECR.
6. The container starts the Python adapter.
7. The adapter connects to Coinbase.
8. The task role supplies temporary Kinesis credentials.
9. The adapter sends unchanged messages to Kinesis.
10. Container logs go to CloudWatch through the execution role.
```

## Why are there two IAM roles?

### ECS task execution role

Used by the ECS/Fargate platform before and while operating the task:

```text
Pull image from ECR
Send container logs to CloudWatch
```

Project role:

```text
lca-coinbase-ecs-execution-role-dev
```

### ECS application task role

Used by the running Python application:

```text
PutRecord and PutRecords
on the exact development Kinesis stream only
```

Project role:

```text
lca-coinbase-ecs-task-role-dev
```

The application receives temporary credentials automatically. No static AWS access key belongs in Python, Docker or GitHub.

## Does ECS prevent a computer from sleeping?

The more accurate statement is:

> An ECS Service attempts to maintain the configured number of running tasks.

For this adapter, the initial design is:

```text
desired count = 1
```

If the running task stops:

```text
Running count becomes 0
    ↓
ECS Service detects it is below desired count 1
    ↓
ECS asks Fargate for a replacement task
    ↓
The replacement pulls the image and starts Python
    ↓
Python reconnects to Coinbase and resumes delivery
```

ECS does not repair the same hidden machine. It requests another task.

## Where does the replacement Fargate task start?

We will configure a VPC and selected subnets:

```text
VPC
├── selected subnet in Availability Zone A
└── selected subnet in Availability Zone B
```

The ECS service scheduler asks Fargate to place the replacement using available capacity in the configured network. A replacement can use a different subnet, Availability Zone, private IP and underlying host. Each Fargate task receives its own elastic network interface.

For a single desired task, this improves replacement options but does not guarantee zero interruption. High availability across zones generally requires more than one independently safe task, which introduces source-subscription, duplication and ordering decisions that must be designed explicitly.

## What happens to Coinbase data during replacement?

There can be a short gap while the new task starts and reconnects:

```text
Old connection stops
    ↓ temporary interruption
New task starts
    ↓
New WebSocket connection begins
```

That is why the adapter needs heartbeat monitoring, reconnect backoff, sequence-gap diagnostics and best-effort recovery. ECS replacement improves availability; it does not by itself guarantee zero source-message loss.

## Could Python run directly on EC2 instead?

Yes.

```text
Coinbase → Python installed on EC2 → Kinesis
```

ECR and ECS would not be mandatory, but the team would manage the EC2 operating system, patches, Python installation, process supervision, recovery, deployments and scaling.

The selected approach is:

```text
ECR → ECS → Fargate
```

because it provides versioned application packages and managed container compute without maintaining EC2 hosts. The trade-off is Fargate cost and less server-level control.

## Could Glue JDBC replace this adapter?

Not for Coinbase.

```text
Database source
    → JDBC URL + credentials + tables
    → Glue can read it

Coinbase source
    → continuous WebSocket messages
    → no JDBC database or tables
    → Python adapter is required
```

Glue belongs later in this architecture:

```text
Coinbase → ECS/Fargate adapter → Kinesis → Glue Streaming/Spark → Silver
```

AWS Glue Streaming supports Kinesis, MSK and Kafka as streaming sources; the external Coinbase WebSocket connection remains the adapter's responsibility.

## What is complete and what is not?

```text
Kinesis stream configuration                 ✅ verified
Kinesis encryption                           ✅ verified
ECS task role and exact-stream simulation    ✅ verified
ECS task execution role configuration        ✅ verified

Kinesis sink inside Python                   ⬜ not implemented
ECR repository and versioned image           ⬜ not created
ECS task definition and service              ⬜ not created
Fargate runtime role assumption              ⬜ not tested
CloudWatch runtime logs                      ⬜ not tested
Real Coinbase-to-Kinesis delivery            ⬜ not tested
```

## Five sentences to remember

1. Python receives Coinbase messages and sends them to Kinesis.
2. Docker packages Python; it does not process the business data.
3. ECR stores the package; it is not a virtual server.
4. Fargate supplies managed compute, while ECS manages the task lifecycle.
5. An ECS Service replaces a stopped task to maintain desired count, but recovery and reconciliation must still be tested.

## Interview preparation

Practice the same concepts from both implementation and architecture perspectives in [`11-ecs-ecr-fargate-data-engineering-architecture-interview-guide.md`](11-ecs-ecr-fargate-data-engineering-architecture-interview-guide.md). It uses Beginner, Medium and Company-scale Scenario modes.

## AWS references

- [Amazon ECS services and task replacement](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html)
- [Amazon ECS service desired count](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service_definition_parameters.html)
- [Fargate task networking](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-task-networking.html)
- [AWS Glue Streaming supported sources](https://docs.aws.amazon.com/glue/latest/dg/streaming-chapter.html)
