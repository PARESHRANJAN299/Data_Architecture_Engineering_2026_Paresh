# 6. Kafka vs Database vs Queue

| Kafka | Database |
|---|---|
| Stores event streams | Stores rows and tables |
| Append-oriented | Insert, update, delete |
| Uses topics | Uses schemas and tables |
| Consumers track offsets | Queries read rows |
| Supports replay | Usually represents state |

Kafka history:
```text
order_created
payment_authorized
order_shipped
order_completed
```

Database row:
```text
order_id = ord-501
status   = completed
```

Traditional queues often remove or hide messages after consumption. Kafka retains events according to policy and allows multiple independent consumers.
