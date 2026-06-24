import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from src.config import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def get_connection():
    """Retorna uma conexão ativa com o banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT,
            database=config.POSTGRES_DB
        )
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar com o banco de dados PostgreSQL: {e}")
        raise

def init_db():
    """
    Inicializa a estrutura lógica do banco de dados criando os schemas (bronze, silver, gold, monitoring)
    e as tabelas físicas iniciais.
    """
    commands = [
        # 1. Criação dos Esquemas (Medalhão + Monitoramento)
        "CREATE SCHEMA IF NOT EXISTS bronze;",
        "CREATE SCHEMA IF NOT EXISTS silver;",
        "CREATE SCHEMA IF NOT EXISTS gold;",
        "CREATE SCHEMA IF NOT EXISTS monitoring;",
        
        # 2. Tabelas do Esquema Bronze (Dados Brutos JSON e Quarentena)
        """
        CREATE TABLE IF NOT EXISTS bronze.raw_realtime (
            id SERIAL PRIMARY KEY,
            collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            payload JSONB NOT NULL,
            processed BOOLEAN DEFAULT FALSE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS bronze.raw_historical (
            id SERIAL PRIMARY KEY,
            collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            payload JSONB NOT NULL,
            days INT,
            processed BOOLEAN DEFAULT FALSE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS bronze.quarantine (
            id SERIAL PRIMARY KEY,
            collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            error_message TEXT,
            rejected_payload JSONB NOT NULL
        );
        """,
        
        # 3. Tabelas de Monitoramento de Pipeline
        """
        CREATE TABLE IF NOT EXISTS monitoring.pipeline_logs (
            id SERIAL PRIMARY KEY,
            job_name VARCHAR(100) NOT NULL,
            started_at TIMESTAMP WITH TIME ZONE NOT NULL,
            finished_at TIMESTAMP WITH TIME ZONE,
            status VARCHAR(20) CHECK (status IN ('SUCCESS', 'FAILURE', 'RUNNING')),
            records_processed INT DEFAULT 0,
            records_failed_quality INT DEFAULT 0,
            error_message TEXT
        );
        """
    ]
    
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        for cmd in commands:
            cur.execute(cmd)
        conn.commit()
        logger.info("Estrutura de banco de dados (schemas, tabelas) inicializada com sucesso.")
        cur.close()
    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()
