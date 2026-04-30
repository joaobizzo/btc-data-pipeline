---

## Domínios e Serviços

### Ingestão de Mercado (Market Intelligence)

Responsável pela coleta de dados externos diretamente da API da CoinGecko.

* **Serviço de Coleta (Realtime)**
  Responsável por coletar preços atuais do Bitcoin (BTC/USD e BTC/BRL) em intervalos regulares utilizando o endpoint `/simple/price`.

* **Serviço de Coleta Histórica (Batch / Backfill)**
  Responsável por recuperar séries temporais históricas utilizando o endpoint `/market_chart`, permitindo reconstrução de dados e preenchimento de lacunas.

---

### Analytics e Transformação

Responsável por processar, padronizar e enriquecer os dados.

* **Serviço de Normalização**
  Converte os dados brutos da camada Bronze em um formato estruturado (timestamps, campos padronizados, etc.).

* **Serviço de Enriquecimento (Câmbio Implícito)**
  Calcula a taxa USD/BRL com base nos preços BTC/USD e BTC/BRL durante a transformação para a camada Silver.

* **Serviço de Granularidade**
  Aplica regras de agregação conforme o tempo:

  * 2h (última semana)
  * 4h (último mês)
  * diário (histórico)

* **Serviço de Backfill**
  Detecta lacunas no histórico e aciona coletas retroativas via endpoint histórico.

---

### Consumo

Responsável por disponibilizar os dados processados.

* **Serviço de Visualização**
  Integração com ferramentas como Metabase para análise e dashboards.

* **Serviço de API / Portfólio**
  Disponibiliza os dados para o seu backend (sistema de carteira de Bitcoin).

---

# Diagrama atualizado (Mermaid)

```mermaid
graph LR

    subgraph DOM_INGESTAO ["Domínio: Ingestão de Mercado"]
        direction TB
        S1["Serviço de Coleta - Realtime BTC USD / BTC BRL"]
        S2["Serviço de Coleta Histórica - Backfill market_chart"]
    end

    subgraph DOM_ANALYTICS ["Domínio: Analytics e Transformação"]
        direction TB
        T1["Serviço de Normalização"]
        T2["Serviço de Enriquecimento - Câmbio Implícito"]
        T3["Serviço de Granularidade - 2h / 4h / Diário"]
        T4["Serviço de Backfill"]
    end

    subgraph DOM_CONSUMO ["Domínio: Consumo"]
        direction TB
        C1["Serviço de Visualização - Metabase"]
        C2["Serviço de API - Portfólio"]
    end

    %% Fluxo de Dados
    S1 --> T1
    S2 --> T1

    T1 --> T2
    T2 --> T3

    T3 <--> T4

    T3 --> C1
    T3 --> C2

```
