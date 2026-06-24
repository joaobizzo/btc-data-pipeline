import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from src.ingestion.pipeline import ingest_historical

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=1),
}

def run_backfill_task(**context):
    """Lê parâmetros de conf passados na trigger manual e executa a ingestão histórica."""
    # Lê 'days' da configuração da DAG. Se não informado, assume 30 dias por padrão.
    dag_run_conf = context.get('dag_run').conf if context.get('dag_run') else {}
    days = dag_run_conf.get('days', 30)
    
    # Valida se days é inteiro válido
    try:
        days = int(days)
    except (ValueError, TypeError):
        days = 30
        
    print(f"Iniciando backfill histórico para os últimos {days} dias...")
    ingest_historical(days=days)

with DAG(
    'btc_historical_backfill',
    default_args=default_args,
    description='Pipeline de Backfill Histórico e Carga em Lote do Bitcoin',
    schedule_interval=None, # Executado manualmente pelo usuário ou via trigger do sistema
    start_date=datetime.datetime(2026, 6, 1),
    catchup=False,
    tags=['bitcoin', 'historical', 'backfill', 'dbt'],
) as dag:

    # 1. Executa a ingestão histórica para popular a camada Bronze
    task_backfill = PythonOperator(
        task_id='run_historical_ingest',
        python_callable=run_backfill_task,
        provide_context=True,
    )

    # 2. Executa as transformações dbt para recalcular as camadas Silver/Gold com os novos dados
    task_dbt_run = BashOperator(
        task_id='dbt_run_reprocess',
        bash_command='dbt run --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project',
    )

    # 3. Executa testes de qualidade pós-transformação
    task_dbt_test = BashOperator(
        task_id='dbt_test_reprocess',
        bash_command='dbt test --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project',
    )

    task_backfill >> task_dbt_run >> task_dbt_test
