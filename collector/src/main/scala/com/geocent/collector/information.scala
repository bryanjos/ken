package com.geocent.collector

import scala.slick.driver.PostgresDriver.simple._
import scala.slick.jdbc.StaticQuery
import scala.slick.lifted.TypeMapper._
import scala.slick.session.Session
import com.typesafe.config.ConfigFactory

case class Information(
	id: Option[Long] = None, 
	source: String, 
	sourceId:String, 
	creator:String, 
	time:Long, 
	location:String = "", 
	lat:Double = 0.0, 
	lon:Double = 0.0, 
	data:String
)

object InformationDAO extends Table[Information]("information") {
  def id = column[Long]("id", O.PrimaryKey, O.AutoInc)
  def source = column[String]("source")
  def sourceId = column[String]("source_id")
  def creator = column[String]("creator")
  def time = column[Long]("time")
  def location = column[String]("location")
  def lat = column[Double]("lat")
  def lon = column[Double]("lon")
  def data = column[String]("data")
  def * = id.? ~ source ~ sourceId ~ creator ~ time ~ location ~ lat ~ lon ~ data <> (Information, Information.unapply _)


  def insertNoId(information:Information)(implicit session:Session) = {
  	val lat = information.lat
  	val lon = information.lon
  	val point = s"ST_GeomFromText('POINT($lat $lon)',4326)"
    val q = (StaticQuery.u + "insert into information (source, sourceId, creator, time, location, lat, lon, data, geom) values (" 
    	+? information.source + "," +? information.sourceId + "," +? information.creator + "," +? information.time + "," +? information.location
    	+ "," +? information.lat + "," +? information.lon + "," +? information.data + "," + point
    	+ ");")
    q.execute
  }

}

trait InformationSource {

	def execute {
		val conf = ConfigFactory.load()
		val database = Database.forURL(conf.getString("db.default.url"), driver = conf.getString("db.default.driver"))

		database withSession { implicit session:Session =>
			val jobs = JobDAO.list
			jobs.map{ job =>
				insertData(getData(job))				
			}		

		}
	}

	def getData(job:Job):Seq[Information]


	def insertData(information:Seq[Information])(implicit session:Session){
		information.map{ info =>
			InformationDAO.insertNoId(info)
		}

	}
}