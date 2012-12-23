package com.geocent.collector

import scala.slick.driver.PostgresDriver.simple._
import scala.slick.jdbc.StaticQuery
import scala.slick.lifted.TypeMapper._
import scala.slick.session.Session
import com.typesafe.config.ConfigFactory

case class Job(
	id:Option[Long], 
	name:String, 
	slug:Option[String], 
	time:Long, 
	location:Option[String], 
	lat:Option[Double], 
	lon:Option[Double], 
	distance:Option[Double],
	tags:String
)


object JobDAO extends Table[Job]("job") {
  def id = column[Long]("id", O.PrimaryKey, O.AutoInc)
  def name = column[String]("name")
  def slug = column[String]("slug")
  def time = column[Long]("time")
  def location = column[String]("location")
  def lat = column[Double]("lat")
  def lon = column[Double]("lon")
  def distance = column[Double]("distance")
  def tags = column[String]("tags")
  def * = id.? ~ name ~ slug.? ~ time ~ location.? ~ lat.? ~ lon.? ~ distance.? ~ tags <> (Job, Job.unapply _)


  def get(id:Long)(implicit session:Session):Option[Job] = {
	  JobDAO.filter(_.id === id).map{e => e}.firstOption()
  }

  def get(slug:String)(implicit session:Session):Option[Job] = {
	  JobDAO.filter(_.slug === slug).map{e => e}.firstOption()
  }

  def insertNoId(job:Job)(implicit session:Session) = {
    val q = (StaticQuery.u + "insert into job (name, slug, time, location, lat, lon, distance, tags) values (" 
    	+? job.name + "," +? job.slug + "," +? job.time + "," +? job.location + "," +? job.lat
    	+ "," +? job.lon + "," +? job.distance + "," +? job.tags + "," + ");")
    q.execute
  }

  def save(job:Job)(implicit session:Session){
    if(job.id == None || job.id.get == 0){
   		val slug = makeSlug(job.name)
      	insertNoId(job.copy(slug = Option[String](slug)))
    }else{
	  	val q = for(i <- JobDAO if i.id === job.id) yield i
	  	q.update(job)
    }
  }

  def list()(implicit session:Session):Seq[Job] = {
		val q = for(job <- JobDAO) yield job
		q.list
  }


  def makeSlug(name:String)(implicit session:Session): String = {

    val proposedSlug = Util.slugify(name)
    
    val jobOp = JobDAO.get(name)

    jobOp.map{
    	val slugCount = JobDAO.slugCount(proposedSlug) 
    	return proposedSlug + slugCount
    }.getOrElse{
		return proposedSlug	
    }
  }
  
  def slugCount(slug:String)(implicit session:Session):Long = {
    val q = StaticQuery.query[(String), Int]("""
        select count(slug) from job where slug like ?
    """)
      q.list(slug + "%").head
  }

}


import scala.annotation.tailrec

object Util {
  def slugify(str: String): String = {
    import java.text.Normalizer
    Normalizer.normalize(str, Normalizer.Form.NFD).replaceAll("[^\\w ]", "").replace(" ", "-").toLowerCase
  }
  
  @tailrec
  def generateUniqueSlug(slug: String, existingSlugs: Seq[String]): String = {
    if (!(existingSlugs contains slug)) {
      slug
    } else {
      val EndsWithNumber = "(.+-)([0-9]+)$".r
      slug match {
        case EndsWithNumber(s, n) => generateUniqueSlug(s + (n.toInt + 1), existingSlugs)
        case s => generateUniqueSlug(s + "-2", existingSlugs)
      }
    }
  }
}