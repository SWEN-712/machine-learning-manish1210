// Databricks notebook source
def requestFormatter(givenTweet:String):String={
  s"""{
    "documents":[
        {
        "language":"en",
        "id":1,
        "text":"${givenTweet}"
        }
    ]
  }"""
}

// COMMAND ----------

def sendPostRequest(textAnalyticsUrl:String,subscriptionKey:String,requestBody:String):String={
  import scalaj.http.Http
  Thread.sleep(3000)
  val result = Http("https://eastus.api.cognitive.microsoft.com/text/analytics/v2.1/sentiment").postData(requestBody)
  .header("Content-Type", "application/json")
  .header("Ocp-Apim-Subscription-Key", "").asString
  result.body
}

// COMMAND ----------

def removeHttpLines(textLine:String):Boolean={
  import scala.util.matching.Regex
  val pattern = "^http".r
  pattern.findFirstIn(textLine) match {
    case Some(x)=>false
    case _ => true
  }
}

// COMMAND ----------

val tweetsSentimentsRdd = sc.textFile("IBMAccess.txt")
.filter(removeHttpLines)
.map(x=>requestFormatter(x))
.map(y=>sendPostRequest("https://eastus.api.cognitive.microsoft.com/text/analytics/v2.1/sentiment","",y))

// COMMAND ----------

val tweetsSentimentList = tweetsSentimentsRdd.collect()

// COMMAND ----------

case class ResponseBody(id:String, score:Double)
case class AzureTextAnalyticsResponse(documents: List[ResponseBody], errors: List[String])

object ResponseJsonUtility extends java.io.Serializable {
 import spray.json._
 import DefaultJsonProtocol._
object MyJsonProtocol extends DefaultJsonProtocol {
 implicit val responseBodyFormat = jsonFormat(ResponseBody,"id","score") //this represents the inner document object of the Json
 implicit val responseFormat = jsonFormat(AzureTextAnalyticsResponse,"documents","errors") //this represents the outer key-value pairs of the Json
 }
//and lastly, a function to parse the Json (string) needs to be written which after parsing the Json string returns data in the form of case class object.
import MyJsonProtocol._
 import spray.json._
 
 def parser(givenJson:String):AzureTextAnalyticsResponse = {
 givenJson.parseJson.convertTo[AzureTextAnalyticsResponse]
 }
}

// COMMAND ----------

val tweetsSentimentScore = tweetsSentimentList.filter(eachResponse=>eachResponse.contains("documents")).map(eachResponse=>ResponseJsonUtility.parser(eachResponse)).map(parsedResponse=>parsedResponse.documents(0).score)

// COMMAND ----------

var pos = 0
var neg = 0
var neutral = 0
for(value <- tweetsSentimentScore){ 
    if(value > 0.5){
      pos+=1
    } 
    else if(value == 0.5){
      neutral+=1
    }
    else{
      neg+=1
    }
}


// COMMAND ----------

case class SentimentAnalysis(category:String, number_of_tweets:Int)
val sentimentEntryDataFrame = sc.parallelize(
 SentimentAnalysis("Positive", pos) ::
 SentimentAnalysis("negative", neg) ::
 SentimentAnalysis("neutral", neutral) ::
 Nil).toDF()
sentimentEntryDataFrame.registerTempTable("test_table")
display(sqlContext.sql("select * from test_table"))
