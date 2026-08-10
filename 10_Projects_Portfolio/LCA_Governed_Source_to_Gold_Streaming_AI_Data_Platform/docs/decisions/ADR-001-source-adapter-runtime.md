# ADR-001 — Use ECS Fargate for the Source Adapter

- **Status:** Accepted for Phase 1
- **Owner:** Paresh Ranjan Rout
- **Decision date:** 2026-08-10

## Context

The first source uses a sustained WebSocket/API connection with reconnect, heartbeat, parsing, batching, and backpressure responsibilities.

## Decision

Run the adapter as an Amazon ECS service on AWS Fargate with a dedicated task role and Secrets Manager integration.

## Alternatives

- Lambda: rejected for the persistent connection lifecycle; retained for bounded control tasks.
- EC2: rejected initially because host management is not justified.
- EKS: rejected initially because Kubernetes platform overhead exceeds the first workload's needs.

## Consequences

- Positive: natural long-running process, container portability, managed hosts, task IAM, health replacement.
- Negative: baseline running cost, container lifecycle, scaling and deployment responsibility.

## Revisit when

Specialized networking/performance, organization-wide Kubernetes, or measured cost changes the balance.
