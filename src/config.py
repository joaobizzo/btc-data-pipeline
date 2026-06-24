import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar arquivo .env se existir (geralmente na raiz do projeto)
ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

class Config:
    # Banco de Dados
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres_password")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "btc_pipeline")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # CoinGecko
    COINGECKO_BASE_URL = os.getenv("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3").rstrip("/")
    COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")

    # Configurações do Streamlit
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", 8501))

config = Config()
