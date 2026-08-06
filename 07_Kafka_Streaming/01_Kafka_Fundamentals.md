# 1. Kafka Fundamentals

## What is Kafka?
Apache Kafka is a distributed event-streaming platform used to send, store, process, and replay events continuously.

```text
Producer -> Kafka -> Consumer
```

### E-commerce example
```text
Order Service -> order-events -> Databricks
```

```json
{"event_id":"evt-1001","event_type":"order_created","order_id":"ord-501","customer_id":"cust-101","amount":149.99}
```

Kafka provides buffering, replay, decoupling, parallel processing, and support for multiple consumers.

## Simple analogy
```text
Kafka          = post office
Topic          = mail category
Message        = letter
Producer       = sender
Consumer       = receiver
Partition      = delivery lane
Offset         = letter position
Consumer group = delivery team
```
