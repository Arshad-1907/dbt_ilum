from pyspark.sql import SparkSession
import subprocess
import mlflow

def run_dbt_transformation():
    # Configure Spark with explicit network settings
    spark = SparkSession.builder \
        .appName("DBT_Spark_Job") \
        .config("spark.driver.bindAddress", "0.0.0.0") \
        .config("spark.driver.host", "127.0.0.1") \
        .getOrCreate()

    try:
        # Install dbt-spark if not already installed
        subprocess.run(["pip", "install", "dbt-spark"], check=True)
        
        # Run dbt transformation
        dbt_result = subprocess.run(
            ["dbt", "run", "--project-dir", "dbt/project", "--profiles-dir", "dbt/profiles"],
            capture_output=True,
            text=True
        )
        print("dbt Output:")
        print(dbt_result.stdout)
        
        if dbt_result.returncode != 0:
            raise RuntimeError(f"dbt run failed: {dbt_result.stderr}")

        # MLflow tracking
        mlflow.start_run(run_name="dbt_run")
        mlflow.log_param("status", "success")
        mlflow.end_run()

        # Verify output
        df = spark.read.parquet("s3a://my-bucket/transformed/transformed_data.parquet")
        print(f"Transformed data count: {df.count()}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    run_dbt_transformation()