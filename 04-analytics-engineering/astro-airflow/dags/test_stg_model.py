from datetime import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig
from cosmos.profiles import GoogleCloudServiceAccountFileProfileMapping

# [START Env Variables] 
CONNECTION_ID = "gcp_conn" 
SCHEMA_NAME = "nyc_taxi"
DBT_ROOT_PATH = '/usr/local/airflow/dags/dbt/taxi_rides_ny'
PROFILE_NAME = "bigquery-conn"
KEYFILE_ROOT  = "/usr/local/airflow/google/credentials/google_credentials.json "

YEAR_DATE = 2019
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
workflow = DAG(
                dag_id="test_stg_model",
                default_args = default_args,
                schedule_interval="0 6 28 * *",
                start_date = datetime(YEAR_DATE, 1, 1),
                end_date = datetime(YEAR_DATE, 12, 30),
                )

profile_config = ProfileConfig(
    profile_name = PROFILE_NAME,
    target_name="dev",
    profile_mapping = GoogleCloudServiceAccountFileProfileMapping(
        conn_id = CONNECTION_ID,
        profile_args = {
            #"keyfile": KEYFILE_ROOT,
            "project": "de-bootcamp-414215",
            "dataset": SCHEMA_NAME
        }
        
    )
)

project_config = ProjectConfig(DBT_ROOT_PATH)

with workflow:
    
    start = EmptyOperator(task_id='start')
    
    dbt_workflow = DbtTaskGroup(
        group_id = 'dbt_workflow',
        project_config = project_config,
        profile_config = profile_config,

    )
    
    finish = EmptyOperator(task_id='finish')

start >> dbt_workflow >> finish
