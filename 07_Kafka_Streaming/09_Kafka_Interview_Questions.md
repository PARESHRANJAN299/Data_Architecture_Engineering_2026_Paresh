# 9. Kafka Interview Questions

1. **What is Kafka?** A distributed event-streaming platform.
2. **What is a topic?** A named stream of related events.
3. **What is a partition?** An ordered subset of a topic enabling parallelism.
4. **Is order guaranteed?** Only within one partition.
5. **What is an offset?** A message position within a partition.
6. **What is a consumer group?** Consumers sharing partitions.
7. **More consumers than partitions?** Extra consumers remain idle.
8. **Why use a key?** To control partitioning and preserve related-event order.
9. **What is consumer lag?** Latest offset minus processed offset.
10. **Does consumption delete events?** No; retention policy controls deletion.
11. **What is replication factor?** Number of copies of each partition.
12. **What is a leader?** Replica handling reads and writes.
13. **What is replay?** Reading old events again by resetting offsets.
14. **What is a DLQ?** A topic for failed records.
15. **What is at-least-once?** Duplicates may occur, but events are not normally lost.
16. **Why idempotency?** To safely handle duplicates.
17. **Why Kafka in data architecture?** Decoupling, buffering, replay, scale, and multiple consumers.
18. **What is rebalancing?** Partition reassignment after consumer membership changes.
19. **Topic vs table?** Event log versus structured state.
20. **Kafka vs queue?** Kafka retains events and supports independent consumers.
