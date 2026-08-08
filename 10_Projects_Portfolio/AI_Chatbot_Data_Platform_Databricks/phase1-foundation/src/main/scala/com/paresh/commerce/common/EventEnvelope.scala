package com.paresh.commerce.common

import java.time.Instant

final case class EventEnvelope(
    event_id: String,
    event_type: String,
    schema_version: String,
    source: String,
    event_time: String,
    ingestion_time: String,
    partition_key: String,
    payload: Map[String, Any]
)

object EventEnvelope {
  def now(
      eventId: String,
      eventType: String,
      source: String,
      partitionKey: String,
      payload: Map[String, Any],
      eventTime: Instant = Instant.now()
  ): EventEnvelope =
    EventEnvelope(
      event_id = eventId,
      event_type = eventType,
      schema_version = "1.0",
      source = source,
      event_time = eventTime.toString,
      ingestion_time = Instant.now().toString,
      partition_key = partitionKey,
      payload = payload
    )
}
