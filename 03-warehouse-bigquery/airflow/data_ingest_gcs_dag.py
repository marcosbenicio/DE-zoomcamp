# [START import modules] 
from airflow import DAG
from datetime import datetime
from google.cloud import storage
from os import getenv

from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.operators.gcs import GCSCreateBucketOperator, GCSListObjectsOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
# [END import modules] 

# [START Env Variables] 
AIRFLOW_HOME = getenv("AIRFLOW_HOME", "/opt/airflow/")
URL_PREFIX = 'https://d37ci6vzurychx.cloudfront.net/trip-data'
FILE_NAME = 'green_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
TABLE_NAME = 'green_taxi_{{ execution_date.strftime(\'%Y_%m\') }}'
URL = f'{URL_PREFIX}/{FILE_NAME}ss'
OUTPUT_FILE_PATH = getenv('OUTPUT_FILE_PATH', f'{AIRFLOW_HOME}/{FILE_NAME}')

PROJECT_ID = getenv("PROJECT_ID", "de-bootcamp-414215")
REGION = getenv("REGIONAL", "us-east1")
LOCATION = getenv("LOCATION", "us-east1")

BUCKET_NAME = getenv("BUCKET_NAME", 'taxi-data-414215')
GCS_BUCKET_PATH = getenv("GCS_BUCKET", f'gs://{BUCKET_NAME}/taxi_data_2022/')
# [END Env Variables] 

# [START default args] 
default_args = {
    "owner": "marcos benicio",
    "email": ['marcosbenicio@id.uff.br'],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1
}
# [END default args]


# [START DAG] 
workflow = DAG(
                dag_id="data_ingest_gcs",
                default_args = default_args,
                tags=['gcs', 'data_ingest'], 
                schedule_interval="0 6 2 * *",
                start_date = datetime(2022, 1, 2),
                end_date = datetime(2022, 12, 2),
                )
# [END DAG]

# [START Workflow] 
with workflow:
    
    download_task = BashOperator(
        task_id="wget_url_data",
        bash_command=f'curl -sSL' + URL + '>' + OUTPUT_FILE_PATH  
    )   
    create_bucket = GCSCreateBucketOperator(
        task_id="create_bucket",
        bucket_name=BUCKET_NAME,
        storage_class="REGIONAL",
        location=LOCATION,
        project_id=PROJECT_ID,
        labels={"env": "dev", "team": "airflow"},
        gcp_conn_id="gcp"
    )
    ingest_data_gcs = LocalFilesystemToGCSOperator(
        task_id="ingest_data_gcs",
        src=OUTPUT_FILE_PATH,
        dst=GCS_BUCKET_PATH,
        bucket=BUCKET_NAME,
        gcp_conn_id="gcp"
    )
    list_bucket_obj = GCSListObjectsOperator(
        task_id = "list_bucket_data",
        bucket=BUCKET_NAME,
        gcp_conn_id="gcp"
    )   
download_task >> create_bucket >> ingest_data_gcs >> list_bucket_obj
# [END Workflow] 