package com.geocent.collector

import com.geocent.collector.sources._
import com.typesafe.config.ConfigFactory

import akka.actor.Actor
import akka.actor.ActorRef
import akka.actor.ActorSystem
import akka.actor.Props
import akka.event.Logging

import akka.actor.ReceiveTimeout
import scala.concurrent.duration._



object Main extends App {
	val system = ActorSystem("Collector")
	val timerActor = system.actorOf(Props[TimerActor], name = "timeractor")
	val conf = ConfigFactory.load()
	val timeout = conf.getInt("polling")

	import system.dispatcher
	val cancellable = system.scheduler.schedule(0 milliseconds, timeout milliseconds, timerActor, "Start")
}


class TimerActor extends Actor {
	import context._

	def receive = {
		case _ =>
			actorOf(Props[TwitterActor]) ! "go"
	}
}