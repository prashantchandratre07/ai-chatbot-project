from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Create Spark session
spark = SparkSession.builder \
    .appName("ChatbotAnalytics") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Define schema
schema = StructType([
    StructField("user_id", StringType(), True),
    StructField("message", StringType(), True),
    StructField("response", StringType(), True),
    StructField("sentiment", StringType(), True)
])

# Read from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "chatbot-topic") \
    .load()

# Convert value to string
json_df = df.selectExpr("CAST(value AS STRING)")

# Parse JSON
parsed_df = json_df \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.user_id", "data.message", "data.response", "data.sentiment")

# Example Analytics: Count sentiments
sentiment_count = parsed_df.groupBy("sentiment").count()

# Output to console
query = sentiment_count.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

query.awaitTermination()