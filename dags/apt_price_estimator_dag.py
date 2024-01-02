from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner':'piotr',
    'retries':0,
    'retry_delay':timedelta(minutes=3)
}

with DAG(
    default_args=default_args,
    dag_id='apt_price_estimator',
    description='get and transform data, train models',
    start_date=datetime(2024, 1, 1),
    schedule='0 3 2 * *',
    catchup=False
) as dag:

    task1 = BashOperator(
        task_id='get_auction_list',
        bash_command='python /opt/airflow/dags/src/get_auction_list.py'
    )

    task1
    