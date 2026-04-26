graph TD

    subgraph Fontes de Dados
        A1[API Bitcoin USD]
        A2[API USD/BRL]
    end

    subgraph Ingestão
        B1[Coletor Python]
        B2[Scheduler / Airflow]
    end

    subgraph Armazenamento
        C1[(Bronze - Dados Brutos)]
        C2[(Silver - Dados Tratados)]
        C3[(Gold - Dados Analíticos)]
    end

    subgraph Processamento
        D1[Transformação - Pandas/dbt]
        D2[Backfill - Recuperação de Dados]
    end

    subgraph Consumo
        E1[Dashboard - Metabase]
        E2[API Portfólio]
    end

    A1 --> B1
    A2 --> B1

    B2 --> B1

    B1 --> C1

    C1 --> D1
    D1 --> C2
    C2 --> C3

    B1 --> D2
    D2 --> C1

    C3 --> E1
    C3 --> E2
