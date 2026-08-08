#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${KAFKA_CONTAINER:-ecommerce-kafka}"
BOOTSTRAP="${KAFKA_BOOTSTRAP:-localhost:9092}"

topics=(
  product-events
  customer-events
  order-events
  payment-events
  inventory-events
  clickstream-events
  commerce-events-dlq
)

echo "Waiting for Kafka..."
for _ in $(seq 1 30); do
  if docker exec "$CONTAINER" /opt/kafka/bin/kafka-topics.sh       --bootstrap-server "$BOOTSTRAP" --list >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

for topic in "${topics[@]}"; do
  docker exec "$CONTAINER" /opt/kafka/bin/kafka-topics.sh     --bootstrap-server "$BOOTSTRAP"     --create     --if-not-exists     --topic "$topic"     --partitions 3     --replication-factor 1
done

echo
echo "Topics:"
docker exec "$CONTAINER" /opt/kafka/bin/kafka-topics.sh   --bootstrap-server "$BOOTSTRAP" --list
