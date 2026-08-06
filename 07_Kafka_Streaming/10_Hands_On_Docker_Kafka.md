# 10. Hands-on Docker Kafka Commands

## Check Kafka
```bash
docker ps --filter name=ecommerce-kafka
```

## Check port mapping
```bash
docker port ecommerce-kafka
```

## List topics
```bash
docker exec ecommerce-kafka   /opt/kafka/bin/kafka-topics.sh   --bootstrap-server localhost:9092   --list
```

## Describe a topic
```bash
docker exec ecommerce-kafka   /opt/kafka/bin/kafka-topics.sh   --bootstrap-server localhost:9092   --describe   --topic order-events
```

## Console producer
```bash
docker exec -it ecommerce-kafka   /opt/kafka/bin/kafka-console-producer.sh   --bootstrap-server localhost:9092   --topic order-events
```

## Console consumer
```bash
docker exec -it ecommerce-kafka   /opt/kafka/bin/kafka-console-consumer.sh   --bootstrap-server localhost:9092   --topic order-events   --from-beginning
```

## Consumer groups
```bash
docker exec ecommerce-kafka   /opt/kafka/bin/kafka-consumer-groups.sh   --bootstrap-server localhost:9092   --list
```
