# Next Step - Databricks Bronze

After this local foundation works, build Databricks Structured Streaming ingestion.

For each topic, Databricks will preserve:

- Kafka key
- Kafka value
- topic
- partition
- offset
- Kafka timestamp
- ingestion timestamp
- parsed envelope
- raw payload

Each stream must have its own checkpoint location.

Suggested first table:

```text
dev_commerce.bronze.product_events_raw
```

The first Databricks validation will compare Kafka offsets with Bronze row counts and prove checkpoint recovery after restart.
