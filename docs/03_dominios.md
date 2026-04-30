## Domínios e Serviços

### Ingestão de Mercado (Market Intelligence)

Responsável pela coleta de dados externos:

- Serviço de Coleta: Responsável por realizar as requisições à API das exchanges e capturar os dados brutos.

- Serviço de Câmbio: Realiza a coleta diária da paridade USD/BRL para permitir a conversão de valores.
* * *

### Analytics e Transformação

Responsável por:

- Serviço de Consolidação: Cruza os dados de BTC (USD) com a taxa de câmbio (BRL) para gerar o preço em moeda nacional.

- Serviço de Granularidade: Aplica as regras de agregação (médias de 2h, 4h e diária) conforme o tempo de vida do dado.

- Serviço de Backfill: Lógica específica para identificar lacunas no histórico e disparar coletas retroativas.
* * *

### Consumo

Responsável por:

- Serviço de Visualização: Camada que conecta o banco de dados ao Metabase.

- Serviço de Notificação: Envia push, e-mail ou mensagem via bot (Telegram/Discord).
* * *

```mermaid
graph LR
    subgraph DOM_INGESTAO [Domínio: Ingestão de Mercado]
        direction TB
        S1[Serviço de Coleta<br/>BTC/USD]
        S2[Serviço de Câmbio<br/>USD/BRL]
    end

    subgraph DOM_ANALYTICS [Domínio: Analytics e Transformação]
        direction TB
        T1[Serviço de Consolidação]
        T2[Serviço de Granularidade<br/>2h / 4h / Diário]
        T3[Serviço de Backfill]
    end

    subgraph DOM_CONSUMO [Domínio: Consumo]
        direction TB
        C1[Serviço de Visualização<br/>Metabase]
        C2[Serviço de Notificação<br/>Telegram/Discord]
    end

    %% Fluxo de Dados
    S1 & S2 --> T1
    T1 --> T2
    T2 <--> T3
    T2 --> C1 & C2
```
