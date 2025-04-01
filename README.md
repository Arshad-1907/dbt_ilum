# dbt + Spark on Ilum Integration

This repository demonstrates how to integrate **dbt** with a Spark cluster managed by **Ilum** using a PySpark job. The project utilizes the Spark adapter for dbt to run SQL-based transformations on Spark, leveraging Ilum for seamless job orchestration, monitoring, and scheduling.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [Local Setup & Testing](#local-setup--testing)
- [Deployment on Ilum](#deployment-on-ilum)
- [Verify & Monitor](#verify--monitor)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Overview

This project demonstrates a complete data pipeline:

- **dbt Project:** Configured to run SQL transformations on Spark via the dbt-spark adapter.
- **PySpark Job:** Automates the execution of dbt commands.
- **Ilum Platform:** Orchestrates and schedules Spark jobs.

## Features

- **dbt + Spark Integration:** Efficiently run SQL-based transformations on Spark.
- **PySpark Automation:** Seamlessly execute dbt transformations via PySpark.
- **Ilum Orchestration:** Simplified deployment, scaling, and job monitoring via Ilum's UI.
- **Configurable Setup:** Quickly update profiles and project configurations.

## Requirements

- **Python 3.11**
- **Anaconda/Conda** (Recommended)
- **Minikube**
- **Helm**
- **kubectl**
- **dbt-core** (1.9.3), **dbt-spark** (1.9.2)
- **PySpark** (3.5.5)
- **protobuf** (3.20.3)
- Optional: **mlflow**

## Project Structure

```
dbt_ilum/
├── dbt_project/
│   ├── models/
│   │   ├── sources.yml
│   │   └── transformed_data.sql
│   ├── dbt_project.yml
│   └── profiles.yml
├── ilum_dbt_job/
│   ├── dbt_trigger_job.py
│   └── dbt/
│       ├── project/      # dbt project files
│       └── profiles/     # dbt profiles
└── generate_data.py
```

## Local Setup & Testing

### Step 1: Environment Setup

Create and activate a conda environment:

```bash
conda create -n dbt_env python=3.11 -y
conda activate dbt_env

pip install pyspark "dbt-spark[session]" mlflow protobuf==3.20.3
```

> **Note:** Adjust or remove mlflow based on your use case.

### Step 2: Start Minikube and Deploy Ilum

Start Minikube with adequate resources:

```bash
minikube start --driver=docker --cpus 4 --memory 8192 --addons metrics-server
```

Deploy Ilum:

```bash
helm repo add ilum https://charts.ilum.cloud
helm repo add jobs-manager https://Delienelu310.github.io/jobs_manager/jobs-manager-helm-repo/
helm repo update

helm install ilum ilum/ilum --namespace ilum --create-namespace
helm install jobsmanager jobs-manager/jobs-manager-helm-chart --namespace ilum
```

Verify pods:

```bash
kubectl get pods -n ilum
```

### Step 3: Configure dbt

Edit your profiles (`~/.dbt/profiles.yml`):

```yaml
dbt_project:
  target: dev
  outputs:
    dev:
      type: spark
      method: session
      host: localhost
      schema: fg
      threads: 1
```

Edit `dbt_project.yml`:

```yaml
name: 'dbt_project'
version: '1.0.0'
config-version: 2
profile: 'dbt_project'
model-paths: ["models"]
```

Test dbt locally:

```bash
cd dbt_project
dbt debug
```

**Setup Visualization:**

![DBT profiles setup](https://github.com/user-attachments/assets/5c52c812-0f88-4447-971a-46a827299697)
![Profiles detail view](https://github.com/user-attachments/assets/3fde9292-028a-4d5e-a0d3-4defa50505a8)

### Step 4: Generate and Upload Data

Create sample data (`generate_data.py`):

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("sample").getOrCreate()
data = [(1, "Alice", 20), (2, "Bob", 17), (3, "Cathy", 25)]
df = spark.createDataFrame(data, ["id", "name", "age"])
df.write.parquet("raw_data.parquet")
```

Run and upload to MinIO at [localhost:9000](http://localhost:9000):

```bash
kubectl port-forward svc/ilum-minio 9000:9000 -n ilum
python generate_data.py
```

Login (user/pass: `minioadmin`) and upload `raw_data.parquet`.

### Step 5: Setup PySpark Job

Create `dbt_trigger_job.py`:

```python
from pyspark.sql import SparkSession
import subprocess

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

    df = spark.read.parquet("s3a://my-bucket/transformed/transformed_data.parquet")
    print(f"Rows processed: {df.count()}")

if __name__ == "__main__":
    run_dbt_transformation()
```

Run locally:

```bash
python dbt_trigger_job.py
```

## Deployment on Ilum

### Step 1: Package Job

```bash
zip -r ilum_dbt_job.zip ilum_dbt_job
```

### Step 2: Submit via Ilum UI

- Port forward Ilum UI:

```bash
kubectl port-forward svc/ilum-ui 9777:9777 -n ilum
```

- Access Ilum UI: [http://localhost:9777](http://localhost:9777)

![Ilum UI](https://github.com/user-attachments/assets/48f5994c-85ff-4a7a-85be-7e55fb448b37)

- Create a new job (Python, Job type):

![Create Job](https://github.com/user-attachments/assets/682b1448-4ba4-44d6-8c94-ee23af95b914)

- Upload zip file, set entry point:

```
dbt_trigger_job.run_dbt_transformation
```

![Upload Code](https://github.com/user-attachments/assets/71d45214-c96f-46d0-bb49-3bd33603a4de)

- Submit job and monitor:

![Monitor Job](https://github.com/user-attachments/assets/1b281bbe-e4e5-475b-8875-874e1c39dea1)

## Verify & Monitor

- **Logs:** Check logs for successful dbt execution.
- **Data:** Verify results in MinIO bucket.

## Troubleshooting

- **Pod Scheduling:** `kubectl describe pod <pod-name> -n ilum`
- **Dependency Issues:** Confirm requirements in Ilum UI.
- **Entry Point Issues:** Ensure entry point naming is correct (omit `.py`).

## Contributing

Contributions are encouraged! Open an issue or pull request for enhancements or fixes.
