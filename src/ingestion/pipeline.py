import datetime
import json
import logging
from psycopg2.extras import Json
from src.database import get_connection, init_db
from src.ingestion.client import CoinGeckoClient
from src.quality.rules import validate_realtime_payload, validate_historical_payload

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def start_pipeline_log(job_name: str) -> int:
    """Insere o log inicial com status 'RUNNING' e retorna o ID do log inserido."""
    conn = get_connection()
    cur = conn.cursor()
    started_at = datetime.datetime.now(datetime.timezone.utc)
    
    cur.execute(
        """
        INSERT INTO monitoring.pipeline_logs (job_name, started_at, status)
        VALUES (%s, %s, 'RUNNING') RETURNING id;
        """,
        (job_name, started_at)
    )
    log_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return log_id

def finish_pipeline_log(log_id: int, status: str, records_processed: int = 0, 
                        records_failed_quality: int = 0, error_message: str = None):
    """Atualiza o log final no banco de dados com os resultados de execução."""
    conn = get_connection()
    cur = conn.cursor()
    finished_at = datetime.datetime.now(datetime.timezone.utc)
    
    cur.execute(
        """
        UPDATE monitoring.pipeline_logs
        SET finished_at = %s, status = %s, records_processed = %s, 
            records_failed_quality = %s, error_message = %s
        WHERE id = %s;
        """,
        (finished_at, status, records_processed, records_failed_quality, error_message, log_id)
    )
    conn.commit()
    cur.close()
    conn.close()

def send_to_quarantine(error_message: str, payload: dict):
    """Envia o payload inválido para a tabela de quarentena para auditoria."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO bronze.quarantine (error_message, rejected_payload)
        VALUES (%s, %s);
        """,
        (error_message, Json(payload))
    )
    conn.commit()
    cur.close()
    conn.close()
    logger.warning(f"Payload inválido enviado para a Quarentena. Erro: {error_message}")

def ingest_realtime():
    """
    Pipeline de Ingestão em Tempo Real.
    Busca o preço atual da CoinGecko, valida a qualidade e insere na camada Bronze.
    """
    job_name = "ingest_realtime"
    logger.info(f"Iniciando job '{job_name}'...")
    
    # 0. Inicializar tabelas se necessário (self-healing)
    init_db()
    
    log_id = start_pipeline_log(job_name)
    client = CoinGeckoClient()
    
    try:
        # 1. Captura de Dados
        payload = client.get_realtime_price()
        
        # 2. Validação da Qualidade
        is_valid, err_msg = validate_realtime_payload(payload)
        
        if is_valid:
            # 3. Persistência na camada Bronze
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO bronze.raw_realtime (payload)
                VALUES (%s);
                """,
                [Json(payload)]
            )
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info("Ingestão Realtime realizada com sucesso.")
            finish_pipeline_log(log_id, "SUCCESS", records_processed=1)
        else:
            # Enviar para a quarentena se falhar nas regras de qualidade
            send_to_quarantine(err_msg, payload)
            finish_pipeline_log(log_id, "FAILURE", records_failed_quality=1, error_message=err_msg)
            
    except Exception as e:
        err_msg = str(e)
        logger.error(f"Erro catastrófico no job '{job_name}': {err_msg}")
        finish_pipeline_log(log_id, "FAILURE", error_message=err_msg)

def ingest_historical(days: int = 7):
    """
    Pipeline de Ingestão Histórica (Backfill).
    Busca séries históricas da CoinGecko, valida a qualidade e insere na camada Bronze.
    """
    job_name = "ingest_historical"
    logger.info(f"Iniciando job '{job_name}' com parâmetro days={days}...")
    
    # 0. Inicializar tabelas se necessário
    init_db()
    
    log_id = start_pipeline_log(job_name)
    client = CoinGeckoClient()
    
    try:
        # 1. Captura de Dados
        payload = client.get_historical_chart(days=days)
        
        # 2. Validação da Qualidade
        is_valid, err_msg = validate_historical_payload(payload)
        
        if is_valid:
            # 3. Persistência na camada Bronze
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO bronze.raw_historical (payload, days)
                VALUES (%s, %s);
                """,
                (Json(payload), days)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            records_count = len(payload.get("usd_prices", []))
            logger.info(f"Ingestão Histórica realizada com sucesso. {records_count} pontos registrados.")
            finish_pipeline_log(log_id, "SUCCESS", records_processed=records_count)
        else:
            send_to_quarantine(err_msg, payload)
            finish_pipeline_log(log_id, "FAILURE", records_failed_quality=1, error_message=err_msg)
            
    except Exception as e:
        err_msg = str(e)
        logger.error(f"Erro catastrófico no job '{job_name}': {err_msg}")
        finish_pipeline_log(log_id, "FAILURE", error_message=err_msg)

if __name__ == "__main__":
    # Teste de execução rápida local
    ingest_realtime()
