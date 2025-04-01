# dbt + Spark on Ilum Integration

This repository demonstrates how to integrate **dbt** with a Spark cluster managed by **Ilum** using a PySpark job. The project uses the Spark adapter for dbt to run SQL-based transformations on Spark, and it leverages Ilum for job orchestration, monitoring, and scheduling.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [Local Setup & Testing](#local-setup--testing)
- [Deployment on Ilum](#deployment-on-ilum)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project demonstrates a complete pipeline where:
- A **dbt project** is configured to run on Spark using the dbt-spark adapter.
- A **PySpark job** (wrapped in an interactive class) triggers the dbt transformations.
- The job is deployed and orchestrated on an Ilum-managed Spark cluster.

## Features

- **dbt + Spark Integration:** Run SQL transformations on Spark using dbt.
- **PySpark Job:** A custom Python script (`dbt_trigger_job.py`) wraps the dbt run command.
- **Ilum Orchestration:** The job is designed to be deployed on Ilum for scalable and scheduled execution.
- **Customizable Configuration:** Easily update dbt profiles and project settings.

## Requirements

- **Python 3.11** (or later)  
- **Anaconda/Conda** (recommended for managing environments)
- **Minikube** (for local Kubernetes cluster testing)
- **Helm** (to deploy Ilum and associated components)
- **dbt-core** (v1.9.3) and **dbt-spark** (v1.9.2)
- **PySpark** (v3.5.5)
- **protobuf==3.20.3** (to resolve compatibility issues)
- (Optional) Other Python libraries as listed in the `requirements.txt` if you create one

## Project Structure

The repository is organized as follows:

## Local Setup & Testing

### 1. Set Up Your Environment

Create and activate a dedicated conda environment (optional but recommended):

```bash
conda create -n dbt_env python=3.11 -y
conda activate dbt_env

pip install pyspark "dbt-spark[session]" mlflow==<compatible-version>  # if using mlflow
pip install "protobuf==3.20.3"

Note: Adjust mlflow version as needed, or remove mlflow-related code if not using it.
```
### 2. Configure dbt

Edit your ~/.dbt/profiles.yml to match the following (adjust values as needed):

```yaml
my_duckdb_project:
  target: dev
  outputs:
    dev:
      type: spark
      method: session
      host: localhost
      schema: fg
      threads: 1
```
Ensure your `dbt_project.yml` (inside `ilum_dbt_job/dbt/project/`) has the profile name set accordingly:

```name: 'my_duckdb_project'
version: '1.0.0'
profile: 'my_duckdb_project'
model-paths: ["models"]
```
Test the dbt connection locally:

```bash
cd ilum_dbt_job/dbt/project
dbt debug
```

3. Test the PySpark Job Locally
Navigate to the root of your job folder and run:

```bash
cd /path/to/ilum_dbt_job
/Users/afsaruddinmohammed/anaconda3/bin/python3 dbt_trigger_job.py
```
You should see output from dbt (e.g., "OK created sql table model ...").

### Deployment on Ilum
### 1. Package Your Job
Zip your ilum_dbt_job folder:

```bash
cd /path/to/
zip -r ilum_dbt_job.zip ilum_dbt_job
```

### 2. Deploy via Ilum UI
Log in to Ilum UI:
<img width="1467" alt="image" src="https://github.com/user-attachments/assets/48f5994c-85ff-4a7a-85be-7e55fb448b37" />

For example, run:

```bash
kubectl port-forward svc/ilum-ui 9777:9777 -n <namespace>
Then open http://localhost:9777 in your browser.
```

Create a New Service/Job:

<img width="1470" alt="image" src="https://github.com/user-attachments/assets/682b1448-4ba4-44d6-8c94-ee23af95b914" />

Go to the Services or Workloads section.

Click New Service (or New Job) and choose Python as the language and Job as the type.

Name it (e.g., "DBT Transform").

<img width="1466" alt="image" src="https://github.com/user-attachments/assets/1b281bbe-e4e5-475b-8875-874e1c39dea1" />

Upload Your Code:

Upload the ilum_dbt_job.zip file.

If the UI doesn’t automatically unzip the archive, include a startup script (e.g., start.sh) in the zip that unzips and then runs your job.

<img width="1331" alt="image" src="https://github.com/user-attachments/assets/71d45214-c96f-46d0-bb49-3bd33603a4de" />

Set the Entry Point:

In the entry point (or job class) field, specify the fully qualified name of your interactive class. For example, if your class is defined in dbt_trigger_job.py and named InteractiveJob, enter:
```
dbt_trigger_job.InteractiveJob
Ensure that the .py extension is omitted.
```
Set Requirements (Optional):

If the UI provides a “Requirements” field, list any additional Python packages (e.g., dbt-spark, mlflow, pyspark) that are not pre-installed in your Docker image.

Start the Job:

Save the configuration and submit/queue the job.

Monitor logs in the Ilum UI to verify that the job starts, executes dbt run, and completes successfully.

### 3. Verify & Monitor
Logs:
Check for messages like "Completed successfully" and "OK created sql table model ..." in the logs.

Data:
Validate that your dbt models are created in the target schema (e.g., fg).

Troubleshooting
Pod Scheduling Issues:
If driver pods remain in Pending, check node resources:

```bash
kubectl get pods -n <namespace>
kubectl describe pod <driver-pod-name> -n <namespace>
```

Module Errors:
Verify dependencies in your environment or add them in the “Requirements” field in the UI.

Entry Point Errors:
Ensure your entry point is set as dbt_trigger_job.InteractiveJob (without the .py extension) and that your file structure is correct.

Contributing
Contributions are welcome! Please open an issue or submit a pull request if you have suggestions or improvements.
