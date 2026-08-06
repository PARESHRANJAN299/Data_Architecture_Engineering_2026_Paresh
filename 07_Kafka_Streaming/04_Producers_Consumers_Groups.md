# 4. Producers, Consumers, and Consumer Groups

## Producer
A producer sends events to Kafka and chooses the topic, key, value, serializer, acknowledgements, and retry behavior.

## Consumer
A consumer reads events. Examples include Databricks, fraud detection, notifications, and monitoring.

## Consumer group
```text
Consumer group: databricks-orders
consumer 1 -> partition 0
consumer 2 -> partition 1
consumer 3 -> partition 2
```

Inside one consumer group, one partition is normally processed by one consumer at a time.

If there are 3 partitions and 5 consumers, 2 consumers remain idle.

## Rebalancing
When consumers join, leave, or fail, Kafka reassigns partitions. This is called rebalancing.
