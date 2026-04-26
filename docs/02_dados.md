
# 📊 Definição e Classificação dos Dados

## 📥 Fontes de Dados

O projeto utiliza a API pública da CoinGecko para obtenção de dados de mercado de criptomoedas.

São utilizadas duas estratégias de coleta:

* * *

### 🔹 Dados em Tempo Quase Real (Preço Atual)

Endpoint:

```
/api/v3/simple/price
```

Parâmetros:

-   `ids=bitcoin`
-   `vs_currencies=usd,brl`
* * *

### 🔹 Dados Históricos (Backfill)

Endpoint:

```
/api/v3/coins/bitcoin/history
```

Parâmetro:

-   `date=dd-mm-yyyy`
* * *

## 📦 Classificação dos Dados

### 🟡 Dados Operacionais (Batch)

-   Histórico diário de preços
-   Utilizados para reconstrução de séries temporais
-   Baixa frequência (1x por dia)
* * *

### 🔵 Dados de Streaming (Simulado)

-   Preços recentes coletados em intervalos de:
    -   2 horas (última semana)
    -   4 horas (último mês)
* * *

# 🧱 Camadas de Dados (Arquitetura Medalhão)

O projeto adota uma abordagem baseada em camadas:

-   **Bronze (dados brutos)**
-   **Silver (dados tratados e normalizados)**
-   _(Gold será implementado posteriormente)_
* * *

# 🥉 Camada Bronze (RAW)

## 📌 Objetivo

Armazenar os dados exatamente como retornados pela API, com o mínimo de transformação possível.

* * *

## 📥 Exemplo de resposta da API (CoinGecko)

### Endpoint: `/simple/price`

```json
{
  "bitcoin": {
    "usd": 117937,
    "brl": 628748
  }
}
```

* * *

### Endpoint: `/history`

```json
{
  "market_data": {
    "current_price": {
      "usd": 115000
    }
  }
}
```

* * *

## 🗃️ Estrutura sugerida (Bronze)

```json
{
  "source": "coingecko",
  "endpoint": "simple_price",
  "collected_at": "2026-04-26T12:00:00Z",
  "payload": {
    "bitcoin": {
      "usd": 117937,
      "brl": 628748
    }
  }
}
```

* * *

## 💡 Características

-   Dados **imutáveis**
-   Sem validação complexa
-   Permite reprocessamento futuro
-   Base para auditoria
* * *

# 🥈 Camada Silver (Dados Tratados)

## 📌 Objetivo

Transformar os dados brutos em um formato estruturado, consistente e pronto para análise.

* * *

## 🔄 Transformações aplicadas

A partir dos dados Bronze:

-   Extração dos campos relevantes
-   Padronização de timestamp
-   Cálculo da taxa de câmbio implícita:

## 💱 Cálculo do câmbio

USD\_BRL = \\frac{BTC\_BRL}{BTC\_USD}

* * *

## 📊 Exemplo de dado Silver

```json
{
  "timestamp": "2025-10-01T16:45:46Z",
  "btc_usd": 117937,
  "btc_brl": 628748,
  "usd_brl": 5.3312,
  "granularity": "2h"
}
```

* * *

## 🧠 Ajustes sugeridos no seu modelo

Seu modelo está bom, mas recomendo pequenas melhorias:

### 🔧 Versão refinada:

```json
{
  "timestamp": "2025-10-01T16:45:46Z",
  "btc_usd": 117937,
  "btc_brl": 628748,
  "usd_brl": 5.3312,
  "granularity": "2h",
  "source": "coingecko"
}
```

* * *

## 💡 Por que essas mudanças?

-   `timestamp` ao invés de `last_updated` → padrão de dados
-   `granularity` → essencial pro seu projeto
-   `source` → rastreabilidade
* * *

# ⚖️ Justificativa da abordagem de câmbio

Ao invés de consumir uma API adicional de câmbio, o projeto calcula a taxa USD/BRL com base nos próprios dados retornados pela CoinGecko:

Vantagens:

-   Redução de custo e chamadas externas
-   Menor acoplamento com múltiplas APIs
-   Consistência entre os valores utilizados

Trade-off:

-   Pequena dependência da precisão do provedor
* * *

