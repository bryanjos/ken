import sbt._
import Keys._

object CollectorBuild extends Build {

  override lazy val settings = super.settings ++
    Seq(
      name := "collector",
      version := "0.1",
      organization := "com.geocent",
      parallelExecution in Test := false,
      scalaVersion := "2.10.0-RC5",
      crossScalaVersions := Seq("2.10.0-RC5"),
      resolvers ++= Seq("Typesafe Repository (releases)" at "http://repo.typesafe.com/typesafe/releases/",
                  "Sonatype OSS Snapshots" at "https://oss.sonatype.org/content/repositories/snapshots",
                  "Spray Repository" at "http://repo.spray.io/"))

  val appDependencies = Seq(
    "com.typesafe" % "config" % "1.0.0",
    "com.typesafe" % "slick_2.10.0-RC1" % "0.11.2",
    "postgresql" % "postgresql" % "9.1-901-1.jdbc4",
    "com.typesafe.akka" % "akka-actor_2.10.0-RC5" % "2.1.0-RC6",
    "io.spray" %%  "spray-json" % "1.2.3" cross CrossVersion.full,
    "com.basho.riak" % "riak-client" % "1.0.6",
    "net.databinder.dispatch" %% "dispatch-core" % "0.9.5"
  )

  lazy val root = Project(id = "collector",
    base = file("."),
    settings = Project.defaultSettings ++ Seq(
      libraryDependencies ++= appDependencies
    )
  )
}