import requests
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
from src.config import config

logger = logging.getLogger(__name__)

class CoinGeckoClient:
    """Cliente HTTP resiliente para consumir dados da API da CoinGecko."""
    
    def __init__(self):
        self.base_url = config.COINGECKO_BASE_URL
        self.api_key = config.COINGECKO_API_KEY
        self.session = requests.Session()
        
        # Se houver chave de API CoinGecko Demo, insere o header necessário
        if self.api_key:
            self.session.headers.update({
                "x-cg-demo-api-key": self.api_key
            })
            logger.info("Chave de API CoinGecko configurada para as requisições.")
        else:
            logger.warning("Nenhuma chave de API CoinGecko informada. Utilizando endpoint público gratuito (sujeito a limites severos de requisições).")

    # Retry Decorator: Tenta até 5 vezes com atraso exponencial (ex: 2s, 4s, 8s, 16s, 32s)
    # Roda apenas em caso de erros de conexão HTTP (timeout, erro do servidor 5xx ou rate-limit 429)
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=(
            retry_if_exception_type(requests.exceptions.ConnectionError) |
            retry_if_exception_type(requests.exceptions.Timeout) |
            retry_if_exception_type(requests.exceptions.HTTPError)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    def _request(self, endpoint: str, params: dict = None) -> dict:
        """Realiza requisição GET genérica com retentativas resilientes."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            # Configura um timeout limite de 10s para não congelar o container
            response = self.session.get(url, params=params, timeout=10)
            
            # Se for código 429 (Rate Limit) ou 5xx (Erro no Servidor), levanta HTTPError para disparar o retry
            if response.status_code == 429:
                logger.warning("CoinGecko retornou HTTP 429 (Rate Limit Excedido). Aguardando para tentar novamente...")
                response.raise_for_status()
            elif response.status_code >= 500:
                logger.warning(f"CoinGecko retornou HTTP {response.status_code} (Erro de Servidor). Aguardando para tentar novamente...")
                response.raise_for_status()
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            # Para erros do tipo 400 ou 404, não adianta retentar. Vamos tratar no caller.
            if e.response is not None and e.response.status_code in [400, 404]:
                logger.error(f"Erro permanente de cliente HTTP {e.response.status_code}: {e}")
                raise e
            logger.warning(f"Erro temporário de HTTP: {e}. Disparando tentativa de reenvio...")
            raise e
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.warning(f"Erro de rede ou timeout: {e}. Disparando tentativa de reenvio...")
            raise e

    def get_realtime_price(self) -> dict:
        """
        Coleta os preços atuais do Bitcoin em USD e BRL.
        Endpoint: /api/v3/simple/price
        """
        params = {
            "ids": "bitcoin",
            "vs_currencies": "usd,brl"
        }
        return self._request("/simple/price", params=params)

    def get_historical_chart(self, days: int = 7) -> dict:
        """
        Coleta dados de séries temporais históricas de preço do Bitcoin em USD e BRL.
        Como CoinGecko retorna apenas uma moeda por requisição no /market_chart,
        fazemos chamadas separadas para USD e BRL e as combinamos.
        Endpoint: /api/v3/coins/bitcoin/market_chart
        """
        params_usd = {
            "vs_currency": "usd",
            "days": days
        }
        params_brl = {
            "vs_currency": "brl",
            "days": days
        }
        
        logger.info(f"Coletando histórico de {days} dias em USD...")
        usd_data = self._request("/coins/bitcoin/market_chart", params=params_usd)
        
        logger.info(f"Coletando histórico de {days} dias em BRL...")
        brl_data = self._request("/coins/bitcoin/market_chart", params=params_brl)
        
        # Combinar as duas respostas de forma a manter uma estrutura unificada Bronze
        return {
            "usd_prices": usd_data.get("prices", []),
            "brl_prices": brl_data.get("prices", []),
            "days": days
        }
