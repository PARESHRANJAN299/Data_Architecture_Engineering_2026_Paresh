# 7. Kafka in Data Architecture

Kafka is usually the event transport and buffering layer.

```text
Source Systems -> Kafka -> Stream Processing -> Lakehouse/Warehouse
```

## E-commerce flow
```text
Open Food Facts API
  -> Scala Product Collector
  -> product-events
  -> Databricks Structured Streaming
  -> Bronze
  -> Silver
  -> Gold
```

## Medallion architecture

### Bronze
Raw payload, topic, partition, offset, event time, and ingestion time.

### Silver
Schema validation, type conversion, deduplication, business rules, late-event handling, and joins.

### Gold
Revenue, customer metrics, product analytics, conversion funnel, inventory risk, and ML features.

## Batch vs streaming
```text
Batch:     Files -> Scheduled Job -> Warehouse
Streaming: Events -> Kafka -> Stream Processor
```
