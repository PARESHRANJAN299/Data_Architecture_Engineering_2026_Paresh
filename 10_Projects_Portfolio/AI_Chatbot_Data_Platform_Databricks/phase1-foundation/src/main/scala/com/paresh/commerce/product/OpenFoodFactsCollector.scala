package com.paresh.commerce.product

import com.paresh.commerce.common.{EventEnvelope, JsonSupport, KafkaPublisher}
import com.typesafe.config.ConfigFactory

import java.net.URI
import java.net.URLEncoder
import java.net.http.{HttpClient, HttpRequest, HttpResponse}
import java.nio.charset.StandardCharsets
import java.time.{Duration, Instant}
import java.util.UUID
import scala.jdk.CollectionConverters._

object OpenFoodFactsCollector {
  private val config = ConfigFactory.load()

  private val client = HttpClient
    .newBuilder()
    .connectTimeout(Duration.ofSeconds(20))
    .build()

  def main(args: Array[String]): Unit = {
    val once = args.contains("--once")
    val publisher = new KafkaPublisher()

    sys.addShutdownHook(publisher.close())

    try {
      var page = 1
      var continue = true

      while (continue) {
        val published = collectPage(page, publisher)
        println(s"Collected page=$page and published=$published product events")

        page = if (page >= 100) 1 else page + 1
        continue = !once

        if (continue) {
          Thread.sleep(config.getLong("openFoodFacts.pollIntervalSeconds") * 1000L)
        }
      }
    } finally {
      publisher.close()
    }
  }

  private def collectPage(page: Int, publisher: KafkaPublisher): Int = {
    val pageSize = config.getInt("openFoodFacts.pageSize")
    val fields = encode(config.getString("openFoodFacts.fields"))
    val url =
      s"${config.getString("openFoodFacts.baseUrl")}?page=$page&page_size=$pageSize&fields=$fields&sort_by=last_modified_t"

    val request = HttpRequest
      .newBuilder(URI.create(url))
      .timeout(Duration.ofSeconds(45))
      .header("Accept", "application/json")
      .header("User-Agent", config.getString("openFoodFacts.userAgent"))
      .GET()
      .build()

    val response = client.send(request, HttpResponse.BodyHandlers.ofString())

    if (response.statusCode() / 100 != 2) {
      throw new RuntimeException(
        s"Open Food Facts request failed: status=${response.statusCode()}"
      )
    }

    val root = JsonSupport.parse(response.body())
    val products = Option(root.get("products"))
      .filter(_.isArray)
      .map(_.elements().asScala.toVector)
      .getOrElse(Vector.empty)

    products.count { product =>
      val code = Option(product.get("code")).map(_.asText()).getOrElse("").trim
      val name = Option(product.get("product_name")).map(_.asText()).getOrElse("").trim

      if (code.isEmpty || name.isEmpty) {
        val dlq = EventEnvelope.now(
          eventId = UUID.randomUUID().toString,
          eventType = "product_rejected",
          source = "open_food_facts",
          partitionKey = if (code.nonEmpty) code else "unknown",
          payload = Map(
            "reason" -> "missing_required_field",
            "raw_product" -> JsonSupport.mapper.convertValue(product, classOf[java.util.Map[String, Object]]).asScala.toMap
          )
        )
        publisher.publish("commerce-events-dlq", dlq.partition_key, dlq)
        false
      } else {
        val sourceModified = Option(product.get("last_modified_t"))
          .filter(_.canConvertToLong)
          .map(node => Instant.ofEpochSecond(node.asLong()))
          .getOrElse(Instant.now())

        val payloadJava =
          JsonSupport.mapper.convertValue(product, classOf[java.util.Map[String, Object]])
        val payload = payloadJava.asScala.toMap

        // The source code plus source modification time makes retries deterministic.
        val eventId = UUID.nameUUIDFromBytes(
          s"$code:${sourceModified.getEpochSecond}".getBytes(StandardCharsets.UTF_8)
        ).toString

        val envelope = EventEnvelope.now(
          eventId = eventId,
          eventType = "product_upserted",
          source = "open_food_facts",
          partitionKey = code,
          payload = payload,
          eventTime = sourceModified
        )

        val metadata = publisher.publish("product-events", code, envelope)
        println(
          s"Published product code=$code topic=${metadata.topic()} partition=${metadata.partition()} offset=${metadata.offset()}"
        )
        true
      }
    }
  }

  private def encode(value: String): String =
    URLEncoder.encode(value, StandardCharsets.UTF_8)
}
