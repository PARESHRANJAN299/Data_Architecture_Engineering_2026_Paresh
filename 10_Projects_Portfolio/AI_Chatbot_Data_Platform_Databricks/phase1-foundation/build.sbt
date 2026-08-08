ThisBuild / scalaVersion := "2.13.16"
ThisBuild / organization := "com.paresh"
ThisBuild / version := "0.1.0"

lazy val root = (project in file("."))
  .settings(
    name := "databricks-ecommerce-phase1",
    libraryDependencies ++= Seq(
      "org.apache.kafka" % "kafka-clients" % "4.2.0",
      "com.fasterxml.jackson.core" % "jackson-databind" % "2.18.3",
      "com.fasterxml.jackson.module" %% "jackson-module-scala" % "2.18.3",
      "com.typesafe" % "config" % "1.4.3",
      "org.slf4j" % "slf4j-simple" % "2.0.17",
      "org.scalatest" %% "scalatest" % "3.2.19" % Test
    ),
    Compile / run / fork := true
  )
