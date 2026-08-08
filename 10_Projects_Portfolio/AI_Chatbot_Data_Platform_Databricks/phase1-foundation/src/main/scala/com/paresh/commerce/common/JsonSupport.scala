package com.paresh.commerce.common

import com.fasterxml.jackson.databind.{JsonNode, ObjectMapper}
import com.fasterxml.jackson.module.scala.DefaultScalaModule

object JsonSupport {
  val mapper: ObjectMapper =
    new ObjectMapper().registerModule(DefaultScalaModule)

  def toJson(value: Any): String =
    mapper.writeValueAsString(value)

  def parse(value: String): JsonNode =
    mapper.readTree(value)
}
