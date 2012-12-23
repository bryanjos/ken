package com.geocent.collector.sources

import com.geocent.collector._
import akka.actor.Actor
import dispatch._
import dispatch.liftjson.Js._


object Twitter extends InformationSource{
	def getData(job:Job):Seq[Information] = {
		val url = "http://search.twitter.com/search.json?q="
		+ job.tags.split(" ").mkString(" OR ")
		+ "&lang=en&count=100"
		+ job.lat.map { job.lat.get + "," + job.lon.get + "," + distance.get + "mi" }.getOrElse{""}

		val LARGE_TWITTER_DATE_FORMAT = "EEE MMM dd HH:mm:ss Z yyyy"
		val format = new java.text.SimpleDateFormat("dd-MM-yyyy")
		val str = Http(host(url) OK as.Json).option

		val results = for {
			JObject(result) <- str
			JField("id_str", JString(is_str)) <- child
			JField("created_at", JString(created_at)) <- child
			JField("from_user", JString(from_user)) <- child			
			JField("text", JString(text)) <- child
			JField("location", JString(location)) <- child
			JField("geo", JArray(geo)) <- child			
		} yield (id_str, created_at, from_user, text, location, geo)

		results.map{ result =>
			Information(
				source = "twitter",
				sourceId = result._1,
				creator = result._3,
				time = new SimpleDateFormat(LARGE_TWITTER_DATE_FORMAT, Locale.ENGLISH).parse(result_2).getMills
				)

		}

		return Seq[Information]()
	}
}

class TwitterActor extends Actor {
	override def preStart() = {
		println("Twitter Starting")
	}

	def receive = {
		case _	=> Twitter.execute
	}
}