import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

from src.clean_data import clean

default_args = {
    'owner':'piotr',
    'retries':0,
    'retry_delay':timedelta(minutes=3),
    'email': [os.environ['PIOTR_EMAIL']],
    'email_on_failure': True,
    'email_on_retry': False,
}

with DAG(
    default_args=default_args,
    dag_id='test_trainer_dag',
    description='testing trainer',
    start_date=datetime(2024, 1, 1),
    schedule='0 3 2 * *',
    catchup=False
) as dag:

    task1 = PythonOperator(
        task_id='clean_data',
        python_callable=clean
    )

    task2 = DockerOperator(
        task_id='test_docker',
        image='trainer:latest',
        container_name='trainer_test',
        api_version='auto',
        auto_remove=True,
        command="python src/clustering.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        mount_tmp_dir=False,
        mounts=[Mount(source='/home/piotr/projects/apartment_price_estimator_v2/trainer',
                      target='/code',
                      type='bind')],
        environment={'MYSQL_PASSWORD': os.environ['MYSQL_PASSWORD'],
                     'PAPUGA_IP': os.environ['PAPUGA_IP']}
    )

    task1 >> task2
