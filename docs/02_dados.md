# 📊 Definição e Classificação dos Dados

## Fontes de Dados

O projeto utiliza a API pública da :contentReference[oaicite:0]{index=0} para obtenção de dados de mercado relacionados ao Bitcoin.

A arquitetura de ingestão utiliza duas estratégias complementares:

- ingestão contínua de baixa latência
- ingestão histórica para reconstrução e backfill

Essa separação permite maior resiliência e recuperação automática de dados perdidos.

---

## 🔹 Dados em Tempo Real (Ingestão Contínua)

Endpoint:

```http
/api/v3/simple/price
```

Parâmetros:

* `ids=bitcoin`
* `vs_currencies=usd,brl`

### Objetivo

Coletar preços atuais do Bitcoin em intervalos regulares para alimentar o pipeline de ingestão contínua.

### Características

* baixa latência
* payload reduzido
* ideal para coleta frequente
* utilizado na camada de ingestão em tempo quase real

### Exemplo de resposta

```json
{
  "bitcoin": {
    "usd": 117937,
    "brl": 628748
  }
}
```

---

## 🔹 Dados Históricos e Backfill

Endpoint:

```http
/api/v3/coins/bitcoin/market_chart
```

Parâmetros:

* `vs_currency=usd` ou `brl`
* `days=N`

### Objetivo

Recuperar séries temporais históricas completas para:

* preenchimento de períodos perdidos
* bootstrap inicial do banco de dados
* sincronização histórica
* reconstrução de séries temporais

### Características

* maior volume de dados
* estrutura temporal contínua
* múltiplos pontos por período
* utilizado na camada batch do pipeline

### Exemplo de resposta

```json
{
  "prices": [
    [1777233625299, 390934.75],
    [1777237256720, 390879.31]
  ]
}
```

### Estrutura dos dados

Cada item do array representa:

```json
[timestamp, price]
```

Onde:

* `timestamp` → Unix timestamp em milissegundos
* `price` → preço do Bitcoin na moeda solicitada

---

# Classificação dos Dados

## Dados Operacionais (Batch)

Dados históricos utilizados para:

* reconstrução de séries temporais
* sincronização de períodos perdidos
* agregações históricas

### Características

* média/baixa frequência
* maior volume de dados
* processamento orientado a histórico

---

## Dados de Streaming (Simulado)

Dados coletados continuamente para atualização recente do sistema.

### Frequência planejada

* 2 horas → última semana
* 4 horas → último mês
* diário → histórico antigo

### Objetivo

Manter maior granularidade em períodos recentes e reduzir volume em períodos antigos.

---

# Camadas de Dados (Arquitetura Medalhão)

O projeto utiliza uma arquitetura baseada no padrão Medalhão:

* 🥉 Bronze → dados brutos
* 🥈 Silver → dados tratados e normalizados
* 🥇 Gold → dados analíticos e agregados (implementação futura)

Essa abordagem melhora:

* rastreabilidade
* reprocessamento
* confiabilidade
* organização do pipeline

---

# 🥉 Camada Bronze (RAW)

## Objetivo

Armazenar os dados exatamente como recebidos pela API, preservando a estrutura original e minimizando transformações.

A camada Bronze funciona como:

* fonte de auditoria
* armazenamento histórico bruto
* base para reprocessamentos futuros

---

## Exemplo Bronze — Tempo Real

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

---

## Exemplo Bronze — Histórico

```json
{
  "source": "coingecko",
  "endpoint": "market_chart",
  "vs_currency": "brl",
  "days": 3,
  "collected_at": "2026-04-26T12:00:00Z",
  "payload": {
    "prices": [
      [1777233625299, 390934.75],
      [1777237256720, 390879.31]
    ]
  }
}
```

---

## Características da Camada Bronze

* dados imutáveis
* sem normalização
* sem agregações
* alta rastreabilidade
* preservação do payload original

---

# 🥈 Camada Silver (Dados Tratados)

## Objetivo

Transformar os dados brutos em registros estruturados e consistentes para análise e consumo interno.

A camada Silver aplica:

* padronização temporal
* normalização de campos
* enriquecimento de dados
* cálculo de métricas derivadas

---

# Transformações Aplicadas

A partir dos dados Bronze:

* extração dos campos relevantes
* conversão de timestamps Unix
* padronização ISO-8601
* consolidação de preços
* classificação de granularidade
* cálculo de câmbio implícito USD/BRL

---

## 💱 Cálculo do câmbio implícito

USD_BRL = \frac{BTC_BRL}{BTC_USD}

---

# Exemplo de dado Silver

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

---

# Melhorias em relação ao dado bruto

## Padronização temporal

* timestamps convertidos para UTC
* formato ISO-8601

## Estrutura consistente

* nomes padronizados
* remoção de estruturas aninhadas

## Enriquecimento

* cálculo de câmbio implícito
* definição de granularidade

---

# Justificativa da abordagem de câmbio

Ao invés de consumir uma API adicional de câmbio, o projeto calcula a taxa USD/BRL utilizando os próprios dados retornados pela CoinGecko.

## Vantagens

* redução de chamadas externas
* menor custo operacional
* menor acoplamento entre provedores
* maior consistência entre os valores utilizados

## Trade-offs

* dependência da precisão do provedor
* pequenas variações em relação ao mercado Forex tradicional

---

# Estratégia Arquitetural de Ingestão

O pipeline utiliza duas estratégias complementares:

## ⚡ Ingestão Contínua

Utiliza `/simple/price` para:

* baixa latência
* atualização frequente
* monitoramento recente

---

## Batch / Backfill

Utiliza `/market_chart` para:

* recuperação de downtime
* sincronização histórica
* reconstrução de períodos faltantes

---

Essa abordagem se aproxima conceitualmente de uma arquitetura Lambda simplificada, separando:

* camada de velocidade (speed layer)
* camada histórica (batch layer)
* camada de consumo analítico

