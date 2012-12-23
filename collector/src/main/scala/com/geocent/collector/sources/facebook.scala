package com.geocent.collector.sources

import com.geocent.collector._
import akka.actor.Actor


object Facebook extends InformationSource{
	def getData(job:Job):Seq[Information] = {
		val url = "https://graph.facebook.com/search?q=coffee&type=post&center=37.76,-122.427&distance=1000"
		return Seq[Information]()
	}
}

class FacebookActor extends Actor {
	override def preStart() = {
		println("Facebook Starting")
	}

	def receive = {
		case _	=> Facebook.execute
	}
}