# Phase 1 Detailed Implementation Plan

## Phase 1 target

Build and prove:

```text
Open Food Facts API
        ↓
Scala product collector
        ↓
Kafka product-events

Scala commerce simulator
        ↓
Kafka business-event topics
        ↓
Databricks Structured Streaming
        ↓
Bronze Delta tables
```

## Workstream 1 - Event contracts

Create one common event envelope:

```json
{
  "event_id": "uuid",
  "event_type": "order_created",
  "schema_version": "1.0",
  "source": "commerce_simulator",
  "event_time": "2026-08-07T00:00:00Z",
  "ingestion_time": "2026-08-07T00:00:01Z",
  "partition_key": "customer-123",
  "payload": {}
}
```

Create contracts for:

- product event
- customer event
- order event
- payment event
- inventory event
- clickstream event
- dead-letter event

## Workstream 2 - Kafka development environment

Create Docker Compose services for:

- Kafka
- optional Kafka UI
- topic initialization

Topics:

```text
product-events
customer-events
order-events
payment-events
inventory-events
clickstream-events
commerce-events-dlq
```

Initial development settings should favor learning and reliability over maximum throughput.

## Workstream 3 - Scala product collector

Responsibilities:

1. call Open Food Facts
2. read selected product fields
3. normalize source values
4. generate a deterministic product event ID
5. add the platform event envelope
6. publish to `product-events`
7. retry temporary HTTP failures
8. respect source limits
9. log request and publish metrics
10. route invalid records to the DLQ

Start with a controlled product sample rather than attempting a full global data copy.

## Workstream 4 - Scala commerce simulator

Generate linked events in business order:

```text
customer created
    ↓
product viewed
    ↓
item added to cart
    ↓
order created
    ↓
payment authorized
    ↓
inventory reduced
    ↓
order completed
```

The simulator must preserve referential relationships:

- orders reference existing customers
- order items reference existing products
- payments reference existing orders
- inventory events reference existing products
- clickstream events reference customers or sessions

## Workstream 5 - Databricks Bronze ingestion

Create one streaming ingestion path per topic or a reusable topic-driven framework.

Bronze tables:

- `bronze_product_events`
- `bronze_customer_events`
- `bronze_order_events`
- `bronze_payment_events`
- `bronze_inventory_events`
- `bronze_clickstream_events`
- `bronze_dead_letter_events`

Each table must include:

- raw Kafka key
- raw Kafka value
- topic
- partition
- offset
- Kafka timestamp
- ingestion timestamp
- parsed envelope fields
- raw payload

## Workstream 6 - Checkpointing and recovery

Each stream uses a separate checkpoint.

Test:

- normal restart
- forced job failure
- Kafka replay
- duplicate publish
- malformed JSON
- temporary source failure

## Workstream 7 - Monitoring

Track:

- API calls
- API failures
- events published
- publish failures
- Kafka throughput
- Kafka lag
- Bronze input rate
- Bronze processing rate
- micro-batch duration
- DLQ count
- freshness

## Phase 1 definition of done

Phase 1 is complete only when:

- the product collector publishes real Open Food Facts events
- the simulator publishes all business event types
- Kafka topics contain valid events
- Databricks writes all topics to Bronze
- checkpoints survive restart
- malformed records are visible in the DLQ
- row counts and offsets reconcile
- README contains run evidence
- setup and recovery steps are documented
