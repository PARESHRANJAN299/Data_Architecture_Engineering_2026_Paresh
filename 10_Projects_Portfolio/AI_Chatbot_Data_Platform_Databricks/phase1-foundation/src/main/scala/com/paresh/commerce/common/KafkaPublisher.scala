package com.paresh.commerce.common

import com.typesafe.config.ConfigFactory
import org.apache.kafka.clients.producer.{KafkaProducer, ProducerRecord, RecordMetadata}
import org.apache.kafka.common.serialization.StringSerializer

import java.time.Duration
import java.util.Properties
import java.util.concurrent.TimeUnit

final class KafkaPublisher extends AutoCloseable {
  private val config = ConfigFactory.load()
  private val props = new Properties()

  props.put("bootstrap.servers", config.getString("kafka.bootstrapServers"))
  props.put("key.serializer", classOf[StringSerializer].getName)
  props.put("value.serializer", classOf[StringSerializer].getName)
  props.put("acks", config.getString("kafka.acks"))
  props.put("retries", config.getInt("kafka.retries").toString)
  props.put("linger.ms", config.getInt("kafka.lingerMs").toString)
  props.put("delivery.timeout.ms", config.getInt("kafka.deliveryTimeoutMs").toString)
  props.put("enable.idempotence", "true")

  private val producer = new KafkaProducer[String, String](props)

  def publish(topic: String, key: String, envelope: EventEnvelope): RecordMetadata = {
    val record = new ProducerRecord[String, String](topic, key, JsonSupport.toJson(envelope))
    producer.send(record).get(30, TimeUnit.SECONDS)
  }

  override def close(): Unit = {
    producer.flush()
    producer.close(Duration.ofSeconds(10))
  }
}
