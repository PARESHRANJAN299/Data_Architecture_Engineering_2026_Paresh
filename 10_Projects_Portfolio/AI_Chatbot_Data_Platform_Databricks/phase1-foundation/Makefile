SHELL := /bin/bash

.PHONY: kafka-up kafka-down topics product-once product-loop simulate consume-products consume-orders test

kafka-up:
	docker compose -f docker/docker-compose.yml up -d
	./scripts/create-topics.sh

kafka-down:
	docker compose -f docker/docker-compose.yml down

topics:
	./scripts/create-topics.sh

product-once:
	sbt "runMain com.paresh.commerce.product.OpenFoodFactsCollector --once"

product-loop:
	sbt "runMain com.paresh.commerce.product.OpenFoodFactsCollector"

simulate:
	sbt "runMain com.paresh.commerce.simulator.CommerceSimulator"

consume-products:
	./scripts/consume-topic.sh product-events

consume-orders:
	./scripts/consume-topic.sh order-events

test:
	sbt test
