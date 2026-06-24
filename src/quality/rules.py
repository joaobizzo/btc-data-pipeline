from typing import Tuple, Any

def validate_realtime_payload(payload: Any) -> Tuple[bool, str]:
    """
    Valida a integridade lógica de um payload em tempo real obtido da CoinGecko.
    Retorna (True, None) se válido, ou (False, "mensagem de erro") caso inválido.
    """
    if not isinstance(payload, dict):
        return False, f"Payload bruto deve ser um dicionário. Recebido: {type(payload)}"
        
    if "bitcoin" not in payload:
        return False, "Campo obrigatório 'bitcoin' ausente no payload."
        
    btc_data = payload.get("bitcoin")
    if not isinstance(btc_data, dict):
        return False, f"Subcampo 'bitcoin' deve ser um dicionário. Recebido: {type(btc_data)}"
        
    for currency in ["usd", "brl"]:
        if currency not in btc_data:
            return False, f"Cotação da moeda '{currency}' ausente no payload de tempo real."
            
        value = btc_data.get(currency)
        if value is None:
            return False, f"Cotação da moeda '{currency}' não pode ser nula."
            
        if not isinstance(value, (int, float)):
            return False, f"Cotação da moeda '{currency}' deve ser numérica. Recebido: {type(value)}"
            
        if value <= 0:
            return False, f"Cotação da moeda '{currency}' deve ser estritamente positiva (> 0). Recebido: {value}"
            
    return True, ""

def validate_historical_payload(payload: Any) -> Tuple[bool, str]:
    """
    Valida a integridade lógica do payload histórico obtido da CoinGecko.
    Retorna (True, None) se válido, ou (False, "mensagem de erro") caso inválido.
    """
    if not isinstance(payload, dict):
        return False, f"Payload histórico bruto deve ser um dicionário. Recebido: {type(payload)}"
        
    for key in ["usd_prices", "brl_prices"]:
        if key not in payload:
            return False, f"Campo obrigatório '{key}' ausente no payload histórico."
            
        prices = payload.get(key)
        if not isinstance(prices, list):
            return False, f"Campo '{key}' deve ser uma lista de preços. Recebido: {type(prices)}"
            
        # Verificar se a lista não está vazia (caso a API não retorne dados históricos válidos)
        if len(prices) == 0:
            return False, f"A lista de preços em '{key}' está vazia."
            
        for i, item in enumerate(prices):
            if not isinstance(item, list) or len(item) != 2:
                return False, f"Registro {i} em '{key}' deve ser um par [timestamp, preço]. Recebido: {item}"
                
            timestamp, price = item
            if not isinstance(timestamp, (int, float)) or not isinstance(price, (int, float)):
                return False, f"Registro {i} em '{key}' possui valores não numéricos: timestamp={timestamp}, preço={price}"
                
            if price <= 0:
                return False, f"Preço no registro {i} em '{key}' deve ser positivo. Recebido: {price}"
                
    return True, ""
