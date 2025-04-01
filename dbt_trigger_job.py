from pyspark.sql import SparkSession
import subprocess
import mlflow

def run_dbt_transformation():
    spark = SparkSession.builder.getOrCreate()
    subprocess.run(["pip", "install", "dbt-spark"], check=True)
    result = subprocess.run(
        ["dbt", "run", "--project-dir", "/dbt/project", "--profiles-dir", "/dbt/profiles"],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f"dbt failed: {result.stderr}")
    mlflow.start_run(run_name="dbt_run")
    mlflow.log_param("status", "success")
    mlflow.end_run()
    df = spark.read.parquet("s3a://my-bucket/transformed/transformed_data.parquet")
    print(f"Rows: {df.count()}")

if __name__ == "__main__":
    run_dbt_transformation()
