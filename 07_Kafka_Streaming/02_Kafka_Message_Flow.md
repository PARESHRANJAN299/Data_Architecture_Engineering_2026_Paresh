# 2. Kafka Message Flow

```text
1. Application creates an event
2. Producer serializes it
3. Producer selects a topic
4. Producer sends a message key
5. Kafka selects a partition
6. Kafka stores the event
7. Kafka assigns an offset
8. Consumer reads the event
9. Consumer processes it
10. Consumer records progress
```

## Project example
```text
Scala commerce simulator
  -> topic: order-events
  -> key: customer-101
  -> partition 1
  -> offset 58
  -> Databricks
  -> Bronze Delta table
```

Kafka sits between systems so producers and consumers do not need to be available at the same time.
