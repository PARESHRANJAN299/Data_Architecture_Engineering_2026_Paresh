package com.paresh.commerce.simulator

import com.paresh.commerce.common.{EventEnvelope, KafkaPublisher}
import com.typesafe.config.ConfigFactory

import java.time.Instant
import java.util.UUID
import scala.util.Random

object CommerceSimulator {
  private val config = ConfigFactory.load()
  private val random = new Random()
  private val productCodes = Vector(
    "3017620422003",
    "5449000000996",
    "7622210449283",
    "8000500310427",
    "3274080005003"
  )

  def main(args: Array[String]): Unit = {
    val maxCycles = args
      .find(_.startsWith("--cycles="))
      .map(_.stripPrefix("--cycles=").toInt)

    val publisher = new KafkaPublisher()
    sys.addShutdownHook(publisher.close())

    try {
      var cycle = 0
      while (maxCycles.forall(cycle < _)) {
        createCommerceJourney(publisher)
        cycle += 1
        Thread.sleep(config.getLong("simulator.intervalMillis"))
      }
    } finally {
      publisher.close()
    }
  }

  private def createCommerceJourney(publisher: KafkaPublisher): Unit = {
    val customerId = s"cust-${random.nextInt(config.getInt("simulator.customerPoolSize")) + 1}"
    val sessionId = UUID.randomUUID().toString
    val productCode = productCodes(random.nextInt(productCodes.size))
    val orderId = s"ord-${UUID.randomUUID()}"
    val paymentId = s"pay-${UUID.randomUUID()}"
    val quantity = random.nextInt(3) + 1
    val unitPrice = BigDecimal(1.99 + random.nextDouble() * 40).setScale(2, BigDecimal.RoundingMode.HALF_UP)
    val total = (unitPrice * quantity).setScale(2, BigDecimal.RoundingMode.HALF_UP)

    publish(
      publisher, "customer-events", customerId, "customer_observed",
      Map("customer_id" -> customerId, "country" -> randomCountry())
    )

    publish(
      publisher, "clickstream-events", customerId, "product_viewed",
      Map(
        "customer_id" -> customerId,
        "session_id" -> sessionId,
        "product_code" -> productCode,
        "channel" -> randomChannel()
      )
    )

    publish(
      publisher, "order-events", customerId, "order_created",
      Map(
        "order_id" -> orderId,
        "customer_id" -> customerId,
        "product_code" -> productCode,
        "quantity" -> quantity,
        "unit_price" -> unitPrice.toDouble,
        "total_amount" -> total.toDouble,
        "currency" -> "USD"
      )
    )

    publish(
      publisher, "payment-events", orderId, "payment_authorized",
      Map(
        "payment_id" -> paymentId,
        "order_id" -> orderId,
        "amount" -> total.toDouble,
        "currency" -> "USD",
        "method" -> randomPaymentMethod()
      )
    )

    publish(
      publisher, "inventory-events", productCode, "inventory_reserved",
      Map(
        "product_code" -> productCode,
        "order_id" -> orderId,
        "quantity_change" -> -quantity,
        "warehouse_id" -> "warehouse-1"
      )
    )
  }

  private def publish(
      publisher: KafkaPublisher,
      topic: String,
      key: String,
      eventType: String,
      payload: Map[String, Any]
  ): Unit = {
    val envelope = EventEnvelope.now(
      eventId = UUID.randomUUID().toString,
      eventType = eventType,
      source = "commerce_simulator",
      partitionKey = key,
      payload = payload,
      eventTime = Instant.now()
    )

    val metadata = publisher.publish(topic, key, envelope)
    println(
      s"Published event=$eventType topic=${metadata.topic()} partition=${metadata.partition()} offset=${metadata.offset()}"
    )
  }

  private def randomCountry(): String =
    Vector("US", "IN", "GB", "DE", "CA")(random.nextInt(5))

  private def randomChannel(): String =
    Vector("web", "ios", "android")(random.nextInt(3))

  private def randomPaymentMethod(): String =
    Vector("card", "wallet", "bank_transfer")(random.nextInt(3))
}
