from datetime import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from cosmos import DbtDag, ProjectConfig, ProfileConfig, DbtTaskGroup
from cosmos.profiles import PostgresUserPasswordProfileMapping
from airflow.providers.postgres.operators.postgres import PostgresOperator


# [START Env Variables] 
CONNECTION_ID = "pg_conn" 
TABLE_NAME = "dbt_test"
SCHEMA_NAME = "public"
DBT_ROOT_PATH = '/usr/local/airflow/dags/dbt/taxi_rides_ny'
# [END Env Variables] 




workflow  =  DAG(
                    dag_id ='dbt_test',
                    start_date=datetime(2024, 1, 1),
                    schedule='@daily'  
                )

with workflow:
    
    init = EmptyOperator(task_id='init')
    
    create_db = PostgresOperator(
                task_id="create_db",
                postgres_conn_id=CONNECTION_ID,
                sql="""CREATE TABLE IF NOT EXISTS dbt_test(
                        id SERIAL PRIMARY KEY);
                    """,
                database="postgres",
            )
    
    profile_config = ProfileConfig(
        profile_name="default",
        target_name="dev",
        profile_mapping=PostgresUserPasswordProfileMapping(
            conn_id=CONNECTION_ID,
            profile_args={
                "host":'astro-airflow_993584-postgres-1',
                "user": 'postgres',
                'password': 'postgres',
                "dbname": 'postgres',
                "schema": SCHEMA_NAME
                },
        ),
    )
    
    
    dbt_workflow = DbtTaskGroup(
        group_id ='dbt_workflow',
        project_config=ProjectConfig(DBT_ROOT_PATH),
        profile_config=profile_config,
        default_args={"retries": 2}
    )
    
    finish = EmptyOperator(task_id='finish')
    
init >> create_db >> dbt_workflow >> finish