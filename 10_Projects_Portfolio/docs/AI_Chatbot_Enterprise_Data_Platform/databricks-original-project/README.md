# AI Chatbot Data Platform — Databricks Lakehouse

An end-to-end, Databricks-first data and AI platform for chatbot telemetry at very high scale. This is deliberately separate from the AWS-native implementation: Databricks owns ingestion, transformation, governance, orchestration, analytics, and AI workflows. Cloud object storage remains the physical storage layer because Databricks runs on a cloud provider.

## Business goal

Give Data Engineering, Analytics, Insights, and AI/ML teams trusted conversation, model, feedback, safety, latency, and token data with near-real-time availability and strong governance.

## Platform choices

- **Unity Catalog** — governance, permissions, lineage, storage access, and the `catalog.schema.table` namespace.
- **Auto Loader** — incremental discovery of new files in the landing location.
- **Delta Lake** — reliable Bronze, Silver, and Gold tables with ACID transactions.
- **Lakeflow Jobs / Declarative Pipelines** — transformation orchestration, retries, data quality rules, and dependency handling.
- **Databricks SQL** — trusted Gold-layer analytics and dashboards.
- **MLflow + Databricks AI services** — experiment tracking, feature/training data, model lifecycle, and retrieval/vector workloads.

## Data flow

`Chatbot events and batch files -> cloud landing storage -> Auto Loader -> Bronze Delta -> Silver Delta -> Gold Delta -> BI, ML, and AI applications`

Auto Loader only discovers and reads new landing files. It does **not** clean or aggregate them. The Bronze-to-Silver and Silver-to-Gold pipeline code does that work.

Read the detailed architecture in [docs/databricks-architecture.md](docs/databricks-architecture.md) and the build order in [docs/build-plan.md](docs/build-plan.md).

## Unity Catalog layout

Use one catalog per environment, not one catalog per team:

```text
chatbot_dev
chatbot_prod
  ├── bronze       # raw, immutable Delta tables
  ├── silver       # validated, deduplicated, conformed tables
  ├── gold         # business-ready facts, aggregates, views
  ├── ml           # training sets, features, registered models
  └── ops          # checkpoints, quarantine, audit/operational tables
```

Example full table name: `chatbot_prod.silver.conversation_events`.

## Reliability principles

1. Keep incoming data immutable in Bronze; never overwrite the raw event history.
2. Use a stable `event_id` and deduplicate in Silver, not by trusting file names.
3. Save a checkpoint for every streaming/Auto Loader query so restarts resume safely.
4. Send invalid records to a quarantine table with an error reason; do not silently drop them.
5. Process incremental downstream changes using Delta Change Data Feed where appropriate.
6. Isolate ingestion, transformation, BI, and ML compute so one workload cannot starve another.
7. Treat event time and late/out-of-order records explicitly with watermarks and replay windows.

## Project status

Architecture and build plan are complete. Cloud resources, pipeline notebooks, and CI/CD will be implemented step by step, starting with Unity Catalog and the Bronze ingest path.
