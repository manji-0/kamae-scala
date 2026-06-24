ThisBuild / scalaVersion := "3.3.8"
ThisBuild / version := "0.1.0-SNAPSHOT"
ThisBuild / organization := "dev.kamae"
ThisBuild / semanticdbEnabled := true
ThisBuild / semanticdbVersion := scalafixSemanticdb.revision
ThisBuild / scalacOptions ++= Seq(
  "-deprecation",
  "-feature",
  "-unchecked",
  "-Xfatal-warnings",
  "-Wunused:all",
  "-Wvalue-discard"
)

lazy val root = (project in file("."))
  .aggregate(taxiRequest)
  .settings(
    name := "kamae-scala",
    publish / skip := true
  )

lazy val taxiRequest = (project in file("skills/kamae-scala/examples"))
  .settings(
    name := "kamae-scala-taxi-request",
    libraryDependencies += "org.scalameta" %% "munit" % "1.1.0" % Test
  )
