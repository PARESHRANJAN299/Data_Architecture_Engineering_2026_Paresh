# 3. Topics, Partitions, Keys, and Offsets

## Topic
A topic is a named stream of related events.

```text
product-events
customer-events
order-events
payment-events
inventory-events
clickstream-events
commerce-events-dlq
```

```text
Kafka topic    = ordered event log
Database table = structured rows
```

## Partition
```text
order-events
├── partition 0
├── partition 1
└── partition 2
```
Partitions provide parallelism. Kafka guarantees ordering only within one partition.

## Message key
Events with the same key normally go to the same partition.

```text
customer-101
├── order_created
├── payment_authorized
└── order_completed
```

## Offset
```text
partition 0
├── offset 0
├── offset 1
└── offset 2
```

```text
latest offset   = 1000
consumer offset = 850
consumer lag    = 150
```
