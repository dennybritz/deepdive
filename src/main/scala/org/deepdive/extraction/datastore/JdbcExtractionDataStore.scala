package org.deepdive.extraction.datastore

import org.deepdive.datastore.JdbcDataStore
import org.deepdive.Logging
import play.api.libs.json._
import scalikejdbc._
import java.io.BufferedReader
import scala.io.Source

trait JdbcExtractionDataStore extends ExtractionDataStore[JsObject] with Logging {

  def ds : JdbcDataStore

  val variableIdCounter = new java.util.concurrent.atomic.AtomicLong(0) 

  def queryAsMap[A](query: String, batchSize: Option[Int] = None)
      (block: Iterator[Map[String, Any]] => A) : A = {
      
      var conn = ds.borrowConnection()
      conn.setAutoCommit(false)
      var stmt = conn.createStatement(java.sql.ResultSet.TYPE_FORWARD_ONLY,
       java.sql.ResultSet.CONCUR_READ_ONLY);
      stmt.setFetchSize(10000);
      var rs = stmt.executeQuery(query)
      var rsmd = rs.getMetaData()
      var columnCount = rsmd.getColumnCount()

      //var m = Map()
      var m:Map[String,Any] = Map()
      var names:Map[Int,String] = Map()

      for ( i <- 1 to columnCount) {
        var name = rsmd.getColumnName(i)
        //println("++ " + name)
        m += (name -> None)
        names += (i -> name)
      }

      var result: List[Map[String, Any]] = List()
      while(rs.next()){
        for ( i <- 1 to columnCount) {
          //var name = rsmd.getColumnName(i)  //TODO: SLOW
          m += (names(i) -> rs.getObject(i))
        }
        result ::= m.mapValues(unwrapSQLType)
      }

      /*
      result = result.map({
        x => 
          x.mapValues(unwrapSQLType)
        })
      */

      block(result.iterator)

      /*
      ds.DB.readOnly { implicit session =>
        val result = SQL(query).map(_.toMap).list.apply().map({
          x => 
            //println(x)
            x.mapValues(unwrapSQLType)
        })
        block(result.iterator)
      }*/
    }

    def queryAsJson[A](query: String, batchSize: Option[Int] = None)
      (block: Iterator[JsObject] => A) : A = {
      queryAsMap(query, batchSize) { iter =>
        val jsonIter = iter.map { row =>
          JsObject(row.mapValues(anyValToJson).toSeq)
        }
        block(jsonIter)
      }
    }

    def unwrapSQLType(x: Any) : Any = {
      x match {
        case x : org.hsqldb.jdbc.JDBCArray => x.getArray().asInstanceOf[Array[_]].toList
        case x : org.hsqldb.jdbc.JDBCClobClient => 
          val reader = new BufferedReader(x.getCharacterStream)
          Stream.continually(reader.readLine()).takeWhile(_ != null).mkString("\n")
        case x : org.hsqldb.jdbc.JDBCBlobClient =>
          val src = Source.fromInputStream(x.getBinaryStream)
          new String(src.getLines.mkString("\n").getBytes, "utf-8")
        case x : org.postgresql.jdbc4.Jdbc4Array => x.getArray().asInstanceOf[Array[_]].toList
        case x : org.postgresql.util.PGobject =>
          x.getType match {
            case "json" => Json.parse(x.getValue)
            case _ => JsNull
          }
        case x => x
      }
    }

    /* Translates an arbitary values that comes back from the database to a JSON value */
    def anyValToJson(x: Any) : JsValue = x match {
      case Some(x) => anyValToJson(x)
      case None | null => JsNull
      case x : String => JsString(x)
      case x : Boolean => JsBoolean(x)
      case x : Int => JsNumber(x)
      case x : Long => JsNumber(x)
      case x : Double => JsNumber(x)
      case x : java.sql.Date => JsString(x.toString)
      case x : Array[_] => JsArray(x.toList.map(x => anyValToJson(x)))
      case x : List[_] => JsArray(x.toList.map(x => anyValToJson(x)))
      case x : JsObject => x      
      case x =>
        log.error(s"Could not convert ${x.toString} of type=${x.getClass.getName} to JSON")
        JsNull
    }

}



