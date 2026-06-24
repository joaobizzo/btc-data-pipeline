import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from src.ingestion.gap_detector import detect_gaps_and_recover

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
}

def gap_check_and_recover_task(**context):
    """Executa a detecção de lacunas e, se recuperar algum dado, registra logs."""
    recovered = detect_gaps_and_recover()
    if recovered:
        print("Dados recuperados pelo detector de lacunas! Prosseguindo para reprocessamento dbt...")
    else:
        print("Nenhuma lacuna crítica detectada. A série temporal está saudável.")
    
    # Compartilha o status com a próxima task via XCom
    context['ti'].xcom_push(key='recovered', value=recovered)

with DAG(
    'btc_auto_recovery',
    default_args=default_args,
    description='Verificação Horária de Lacunas e Auto-Recuperação de Dados (Feedback Loop)',
    schedule_interval='0 * * * *', # Executa de hora em hora
    start_date=datetime.datetime(2026, 6, 1),
    catchup=False,
    tags=['bitcoin', 'auto-recovery', 'feedback-loop'],
) as dag:

    # 1. Checa gaps na série temporal da Silver e executa backfill se necessário
    task_check_gaps = PythonOperator(
        task_id='check_gaps_and_backfill',
        python_callable=gap_check_and_recover_task,
        provide_context=True,
    )

    # 2. Executa as transformações dbt
    task_dbt_run = BashOperator(
        task_id='dbt_run_auto',
        bash_command='dbt run --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project',
    )

    # 3. Executa os testes dbt
    task_dbt_test = BashOperator(
        task_id='dbt_test_auto',
        bash_command='dbt test --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project',
    )

    task_check_gaps >> task_dbt_run >> task_dbt_test
