from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("sample").getOrCreate()
data = [(1, "Alice", 20), (2, "Bob", 17), (3, "Cathy", 25)]
df = spark.createDataFrame(data, ["id", "name", "age"])
df.write.parquet("raw_data.parquet")
