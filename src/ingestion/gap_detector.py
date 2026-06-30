import logging
from src.database import get_connection
from src.ingestion.pipeline import ingest_historical

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def detect_gaps_and_recover() -> bool:
    """
    Detecta lacunas de séries temporais nas tabelas da camada Silver nos últimos 7 dias.
    Se detectar uma lacuna maior que 4 horas (14400 segundos), ou se a tabela estiver vazia,
    dispara automaticamente a ingestão histórica (Backfill) dos últimos 7 dias.
    Retorna True se um backfill foi acionado, False caso contrário.
    """
    logger.info("Iniciando verificação de lacunas de dados na camada Silver...")
    
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # 1. Verifica se a tabela está vazia (bootstrap)
        cur.execute("SELECT COUNT(*) FROM silver.silver_prices;")
        count = cur.fetchone()[0]
        
        if count == 0:
            logger.warning("Camada Silver está totalmente vazia! Disparando backfill inicial de 15 dias.")
            cur.close()
            conn.close()
            # Dispara backfill
            ingest_historical(days=15)
            return True
            
        # 2. Verifica lacunas temporais nos últimos 7 dias
        # Calcula a diferença de tempo entre registros consecutivos
        query = """
        WITH time_diffs AS (
            SELECT 
                price_timestamp,
                LEAD(price_timestamp) OVER (ORDER BY price_timestamp) AS next_timestamp
            FROM silver.silver_prices
            WHERE price_timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days'
        )
        SELECT 
            price_timestamp,
            next_timestamp,
            EXTRACT(EPOCH FROM (next_timestamp - price_timestamp)) AS diff_seconds
        FROM time_diffs
        WHERE next_timestamp IS NOT NULL
        ORDER BY diff_seconds DESC
        LIMIT 1;
        """
        
        cur.execute(query)
        row = cur.fetchone()
        
        # Limite tolerável: 4 horas (14400 segundos) de gap
        gap_limit_seconds = 14400 
        
        if row:
            price_ts, next_ts, diff_seconds = row
            if diff_seconds > gap_limit_seconds:
                logger.warning(
                    f"Lacuna crítica de dados detectada! Sem dados entre {price_ts} e {next_ts} "
                    f"({round(diff_seconds / 3600.0, 2)} horas). Disparando backfill corretivo automático de 7 dias..."
                )
                cur.close()
                conn.close()
                ingest_historical(days=7)
                return True
            else:
                logger.info(f"Nenhum gap crítico encontrado. Maior intervalo recente: {round(diff_seconds / 60.0, 2)} minutos.")
        else:
            logger.info("Dados insuficientes nos últimos 7 dias para analisar gaps, mas há histórico antigo.")
            
        cur.close()
    except Exception as e:
        logger.error(f"Erro ao executar o detector de lacunas: {e}")
    finally:
        if conn:
            conn.close()
            
    return False

if __name__ == "__main__":
    detect_gaps_and_recover()
