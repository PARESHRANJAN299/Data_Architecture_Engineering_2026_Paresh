# Build plan — Databricks Lakehouse

1. **Foundation:** create the Unity Catalog metastore objects, `chatbot_dev` catalog, schemas, storage credential, external location, and least-privilege groups.
2. **Bronze:** land sample chatbot events in a governed landing volume and create an Auto Loader pipeline with a checkpoint and schema location.
3. **Silver:** validate schema, deduplicate by `event_id`, standardize timestamps, create a quarantine table, and add data-quality expectations.
4. **Gold:** create daily product, model-performance, token-cost, and safety metric tables using incremental changes.
5. **AI/ML:** create approved training views, embedding pipeline, vector index, MLflow experiment, and model registration flow.
6. **Serving:** expose Gold data through Databricks SQL and expose approved model/vector retrieval through governed endpoints.
7. **Operate:** configure alerts, system-table dashboards, job retries, backfill procedure, CI/CD, and disaster-recovery runbooks.

Each stage must be tested with: a normal event, a duplicate event, a late event, an invalid event, and a pipeline restart.
