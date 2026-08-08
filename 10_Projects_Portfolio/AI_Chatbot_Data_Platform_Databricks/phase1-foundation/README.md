# Phase 1 Foundation

This is the first executable step of the Databricks e-commerce streaming project.

## What this step builds

```text
Open Food Facts API → Scala product collector → Kafka product-events

Scala commerce simulator → Kafka customer/order/payment/inventory/clickstream topics
```

Databricks Bronze ingestion is the next step after the local event flow is proven.

## Prerequisites

- Docker Desktop
- Java 17 or newer
- sbt
- Git

Check:

```bash
docker --version
java -version
sbt --version
```

## Start Kafka

```bash
make kafka-up
```

The project uses the official Apache Kafka 4.2.0 JVM image in single-node KRaft mode for local development.

## Publish real product events

Run one Open Food Facts page:

```bash
make product-once
```

Run continuously:

```bash
make product-loop
```

The collector requests only selected fields, uses pagination, sends a User-Agent header, and creates deterministic event IDs from product code plus source modification time.

## Generate commerce events

```bash
make simulate
```

For a short run:

```bash
sbt "runMain com.paresh.commerce.simulator.CommerceSimulator --cycles=10"
```

## Inspect Kafka

Products:

```bash
make consume-products
```

Orders:

```bash
make consume-orders
```

Any topic:

```bash
./scripts/consume-topic.sh payment-events
```

## Topics

- `product-events`
- `customer-events`
- `order-events`
- `payment-events`
- `inventory-events`
- `clickstream-events`
- `commerce-events-dlq`

## Definition of done

This step is complete when:

- Kafka starts successfully.
- All seven topics exist.
- Open Food Facts records appear in `product-events`.
- Linked simulated business events appear in their topics.
- Invalid product records appear in `commerce-events-dlq`.
- Restarting the applications does not change deterministic product event identity.
