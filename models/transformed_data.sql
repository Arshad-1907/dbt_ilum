{{ config(materialized='table', location='s3a://my-bucket/transformed/transformed_data.parquet') }}
SELECT 
  id,
  name,
  age + 1 as incremented_age
FROM {{ source('ilum_data', 'raw_data') }}
WHERE age > 18
