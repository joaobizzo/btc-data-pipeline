import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from src.ingestion.pipeline import ingest_realtime

# Configurações de retentativas padrão da DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': datetime.timedelta(seconds=30),
}

with DAG(
    'btc_ingestion_and_transform',
    default_args=default_args,
    description='Pipeline de Captura e Transformação dbt do Bitcoin (Tempo Real)',
    schedule_interval='*/5 * * * *', # Executa a cada 5 minutos
    start_date=datetime.datetime(2026, 6, 1),
    catchup=False,
    tags=['bitcoin', 'realtime', 'dbt'],
) as dag:

    # 1. Ingestão dos dados da CoinGecko (Bronze)
    task_ingest = PythonOperator(
        task_id='ingest_raw_data',
        python_callable=ingest_realtime,
    )

    # 2. Execução das transformações do dbt (Silver & Gold)
    task_dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='dbt run --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project',
    )

    # 3. Execução dos testes de qualidade do dbt
    task_dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='dbt test --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project',
    )

    # Fluxo de execução
    task_ingest >> task_dbt_run >> task_dbt_test
