#!/usr/bin/env bash
set -euo pipefail

TOPIC="${1:-product-events}"
CONTAINER="${KAFKA_CONTAINER:-ecommerce-kafka}"

docker exec -it "$CONTAINER" /opt/kafka/bin/kafka-console-consumer.sh   --bootstrap-server localhost:9092   --topic "$TOPIC"   --from-beginning   --property print.key=true   --property key.separator=" | "
