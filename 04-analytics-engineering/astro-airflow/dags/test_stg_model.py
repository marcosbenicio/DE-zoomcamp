from datetime import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig
from cosmos.profiles import GoogleCloudServiceAccountFileProfileMapping

# [START Env Variables] 
CONNECTION_ID = "gcp_conn" 
SCHEMA_NAME = "nyc_taxi"
DBT_ROOT_PATH = '/usr/local/airflow/dags/dbt/taxi_rides_ny'
PROFILE_NAME = "taxi_rides_ny"
KEYFILE_ROOT  = "/usr/local/airflow/google/credentials/google_credentials.json "
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

workflow  =  DAG(
                    dag_id ='test_stg_model',
                    start_date=datetime(2024, 1, 1),
                    schedule='@daily',
                    default_args=default_args  
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
        
    init = EmptyOperator(task_id='init')
    
    dbt_workflow = DbtTaskGroup(
        group_id = 'dbt_workflow',
        project_config = project_config,
        profile_config = profile_config,

    )
    
    finish = EmptyOperator(task_id='finish')

init >> dbt_workflow >> finish
