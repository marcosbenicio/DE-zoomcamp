# [START import modules]-----------------------------------------------------------------------------------------  
from airflow import DAG
from datetime import datetime
from google.cloud import storage
import pandas as pd
import re
import pyarrow.parquet as pq
import pyarrow as pa
from os import getenv

from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.gcs import GCSCreateBucketOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator,\
    BigQueryCreateEmptyDatasetOperator
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig
from cosmos.profiles import GoogleCloudServiceAccountFileProfileMapping
# [END import modules] 

# [START Env Variables]----------------------------------------------------------------------------------------- 
##From https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page##
URL_PREFIX_1 = 'https://d37ci6vzurychx.cloudfront.net/trip-data'
URL_PREFIX_2 = 'https://d37ci6vzurychx.cloudfront.net/trip-data'
FILE_NAME_1 = 'green_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
FILE_NAME_2 = 'yellow_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'

URL_1 = f'{URL_PREFIX_1}/{FILE_NAME_1}'
URL_2 = f'{URL_PREFIX_2}/{FILE_NAME_2}'

AIRFLOW_HOME = getenv("AIRFLOW_HOME", "/usr/local/airflow")
FILE_PATH_1 = getenv('FILE_PATH_1', f'{AIRFLOW_HOME}/{FILE_NAME_1}')
FILE_PATH_2 = getenv('FILE_PATH_2', f'{AIRFLOW_HOME}/{FILE_NAME_2}')

DATASET_NAME= getenv("DATASET_NAME", 'nyc_taxi')               
TABLE_NAME = 'green_taxi_{{ execution_date.strftime(\'%Y_%m\') }}' 
YEAR = 2019
TABLE_ID_1 = f"green_taxi_external_{YEAR}"
TABLE_ID_2 = f"yellow_taxi_external_{YEAR}"

PROJECT_ID = getenv("PROJECT_ID", "de-bootcamp-414215")
REGION = getenv("REGIONAL", "us-east1")
LOCATION = getenv("LOCATION", "us-east1")

BUCKET_NAME = getenv("BUCKET_NAME", 'nyc-taxi-data-414215')
GCS_BUCKET_FOLDER= getenv("GCS_BUCKET", f'nyc_taxi_trip_{YEAR}')
CONNECTION_ID = getenv("CONNECTION_ID", "gcp_conn")
SCHEMA_NAME = "nyc_taxi"
DBT_ROOT_PATH = '/usr/local/airflow/dags/dbt/taxi_rides_ny'
PROFILE_NAME = "bigquery-db"
# [END Env Variables] 

# [START default args]-----------------------------------------------------------------------------------------  
default_args = {
    "owner": "marcos benicio",
    "email": ['marcosbenicio@id.uff.br'],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1
}
# [END default args]

# [START Python Functions]----------------------------------------------------------------------------------------- 
def transform_columns_to_snake(file_path):
    
    # Load the parquet file metadata (schema) without reading the data
    original_table = pq.read_table(file_path)
    original_column_names = original_table.schema.names
    original_metadata = original_table.schema.metadata
    
    # convert all camel columns names to snake
    def camel_to_snake(name):
        return re.sub(r'(?<=[a-z0-9])([A-Z])|(?<=[A-Z])([A-Z])(?=[a-z])', r'_\g<0>', name).lower()
    
    new_column_names = [camel_to_snake(name) for name in original_column_names]
    fields = [pa.field(new_name, original_table.schema.field(original_name).type) 
                for new_name, original_name in zip(new_column_names, original_column_names)]
    
    new_schema = pa.schema(fields, metadata=original_metadata)
    
    new_table = pa.Table.from_arrays(original_table.columns, schema=new_schema)

    pq.write_table(new_table, file_path)

# Takes 20 mins, at an upload speed of 800kbps. Faster if your internet has a better upload speed 
def filesystem_to_gcs(bucket, dst, src):
    """
    Uploads a file from the local filesystem to Google Cloud Storage.
    
    :param bucket: Name of the GCS bucket.
    :param dst: Destination path & file-name within the GCS bucket.
    :param src: Source path path & file-name on the local filesystem.
    """
    # Adjust the maximum multipart upload size and chunk 
    # to prevent timeout for files > 6 MB on 800 kbps upload speed.
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB

    # Initialize the GCS client and get the bucket
    client = storage.Client()
    bucket = client.bucket(bucket)

    # Create a blob object and upload the file
    blob = bucket.blob(dst)
    blob.upload_from_filename(src)

    print(f"File {src} uploaded to {dst} in bucket {bucket}.")
# [END Python Functions]

# [START DAG Object]-----------------------------------------------------------------------------------------  
workflow = DAG(
                dag_id="inget_nyc_taxi_gcs",
                default_args = default_args,
                description="""A DAG to export data from NYC taxi web, 
                load the taxi trip data into GCS to create a BigQuery external table """,
                tags=['gcs', 'bigquery','data_elt', 'dbt', 'nyc_taxi'], 
                schedule_interval="0 6 28 * *",
                start_date = datetime(YEAR, 1, 1),
                end_date = datetime(YEAR, 12, 30),
                )
# [END DAG Object]

# [START Workflow]----------------------------------------------------------------------------------------- 

# Start the workflow
with workflow:
    
    download_data = BashOperator(
        task_id="download_data",
        bash_command =  f"""    
                        curl -sSLo {FILE_PATH_1} {URL_1} && \\
                        curl -sSLo {FILE_PATH_2} {URL_2}
                        """
    )
    transform_green_taxi_columns_to_snake = PythonOperator(
        task_id='transform_green_taxi_columns_to_snake',
        python_callable=transform_columns_to_snake,
        op_kwargs={'file_path': FILE_PATH_1},
    )
    transform_yellow_taxi_columns_to_snake = PythonOperator(
        task_id='transform_yellow_taxi_columns_to_snake',
        python_callable=transform_columns_to_snake,
        op_kwargs={'file_path': FILE_PATH_2},
    )   
    create_bucket = GCSCreateBucketOperator(
        task_id="create_bucket",
        bucket_name=BUCKET_NAME,
        storage_class="REGIONAL",
        location=LOCATION,
        project_id=PROJECT_ID,
        labels={"env": "dev", "team": "airflow"},
        gcp_conn_id= CONNECTION_ID
    )
    ingest_green_taxi_gcs = PythonOperator(
        task_id="ingest_green_taxi",
        python_callable=filesystem_to_gcs,
        op_kwargs={ "bucket": BUCKET_NAME, 
                    "dst": f"{GCS_BUCKET_FOLDER}/{FILE_NAME_1}", 
                    "src": FILE_PATH_1
                    }
    )
    ingest_yellow_taxi_gcs = PythonOperator(
        task_id="ingest_yellow_taxi",
        python_callable=filesystem_to_gcs,
        op_kwargs={ "bucket": BUCKET_NAME, 
                    "dst": f"{GCS_BUCKET_FOLDER}/{FILE_NAME_2}", 
                    "src": FILE_PATH_2
                    }
    )
    create_empty_dataset = BigQueryCreateEmptyDatasetOperator(
        task_id="create_empty_dataset",
        dataset_id=DATASET_NAME,
        project_id=PROJECT_ID,
        location=LOCATION,
        gcp_conn_id= CONNECTION_ID
    )
    bigquery_green_taxi_table = BigQueryCreateExternalTableOperator(
        task_id="create_green_taxi_table",
        table_resource={
            'tableReference': {
                'projectId': PROJECT_ID,
                'datasetId': DATASET_NAME,
                'tableId': TABLE_ID_1,
            },
            'externalDataConfiguration': {
                'sourceFormat': 'PARQUET',
                'sourceUris': [f"gs://{BUCKET_NAME}/{GCS_BUCKET_FOLDER}/green_tripdata_*.parquet"],
                'autodetect': True 
                }
        },
        gcp_conn_id= CONNECTION_ID
    )
    bigquery_yellow_taxi_table = BigQueryCreateExternalTableOperator(
        task_id="create_yellow_taxi_table",
        table_resource={
            'tableReference': {
                'projectId': PROJECT_ID,
                'datasetId': DATASET_NAME,
                'tableId': TABLE_ID_2,
            },
            'externalDataConfiguration': {
                'sourceFormat': 'PARQUET',
                'sourceUris': [f"gs://{BUCKET_NAME}/{GCS_BUCKET_FOLDER}/yellow_tripdata_*.parquet"],
                'autodetect': True
            }
        },
        gcp_conn_id= CONNECTION_ID
    )
download_data >> [transform_green_taxi_columns_to_snake, transform_yellow_taxi_columns_to_snake] \
>> create_bucket >> [ingest_green_taxi_gcs, ingest_yellow_taxi_gcs ] \
>> create_empty_dataset >> [bigquery_yellow_taxi_table, bigquery_green_taxi_table]
# [END Workflow] 