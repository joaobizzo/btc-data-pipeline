# Walkthrough da Implementação - Prova 2 (BTC Data Pipeline)

Este documento resume a implementação final do protótipo do ciclo de vida de engenharia de dados do **BTC Data Pipeline** conforme aprovado no plano de implementação e adequado aos feedbacks da Prova 1.

---

## 🚀 O que foi Implementado

### 1. Reestruturação Conceitual (Feedbacks da Prova 1)
*   **Domínios de Negócio:** Em [docs/03_dominios.md](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/docs/03_dominios.md), os limites organizacionais foram redefinidos sob a perspectiva de negócio: *Inteligência de Mercado*, *Conversão Cambial*, *Métricas e Analytics Temporal* e *Portfólio/Consumo*.
*   **Arquitetura As-Built:** Em [docs/04_arquitetura.md](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/docs/04_arquitetura.md), a arquitetura foi expandida para incluir quarentena de qualidade, logs de monitoramento e retroalimentações (autocura).
*   **Seleção de Tecnologias:** Em [docs/05_tecnologias.md](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/docs/05_tecnologias.md), cada escolha tecnológica foi profundamente justificada (Postgres, Airflow, dbt, Streamlit) e detalhou-se o funcionamento transversal de qualidade, monitoramento e governança.

### 2. Infraestrutura Docker e Configurações
*   [docker-compose.yml](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/docker-compose.yml): Configuração robusta e integrada com Postgres (dados e metadados), Airflow (LocalExecutor com webserver e scheduler) e Streamlit.
*   [Dockerfile.airflow](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/Dockerfile.airflow) e [Dockerfile.streamlit](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/Dockerfile.streamlit): Imagens customizadas pré-configuradas com todas as dependências especificadas no [requirements.txt](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/requirements.txt).
*   [.env.example](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/.env.example) e [.gitignore](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/.gitignore): Segregação de segredos locais e exclusão de lixos de build no versionamento.

### 3. Conexão, Ingestão e Qualidade (Camada Bronze)
*   [src/database.py](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/src/database.py): Módulo auto-executável de conexão que inicializa automaticamente os schemas `bronze`, `silver`, `gold` e `monitoring` no Postgres se eles não existirem (auto-recuperação/resiliência).
*   [src/ingestion/client.py](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/src/ingestion/client.py): Cliente CoinGecko contendo lógica de *Exponential Backoff* e tratamentos HTTP (resiliência contra rate-limit 429).
*   [src/quality/rules.py](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/src/quality/rules.py): Validação em tempo de execução para tipos de dados, chaves nulas e valores de preços negativos.
*   [src/ingestion/pipeline.py](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/src/ingestion/pipeline.py): Pipeline que injeta dados em tempo real ou históricos. Dados inválidos são jogados para a quarentena (`bronze.quarantine`) e erros ou sucessos são registrados na tabela `monitoring.pipeline_logs`.

### 4. Transformações e Qualidade Analítica (Camadas Silver & Gold com dbt)
*   [dbt_project/profiles.yml](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/dbt_project/profiles.yml) e [dbt_project/dbt_project.yml](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/dbt_project/dbt_project.yml): Projeto dbt configurado.
*   [silver_prices.sql](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/dbt_project/models/silver/silver_prices.sql): Processa payloads brutos JSON da realtime e historical, realiza deduplicação estrita por timestamp mantendo a mais recente e calcula a taxa de câmbio implícita USD/BRL.
*   Modelos Gold ([2h](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/dbt_project/models/gold/prices_aggregated_2h.sql), [4h](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/dbt_project/models/gold/prices_aggregated_4h.sql), [daily](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/dbt_project/models/gold/prices_aggregated_daily.sql)): Realiza a agregação (downsampling) da série histórica aplicando funções de agregados e contagem de registros por janela.
*   **Testes Integrados:** Configurados nos schemas YAML ([Silver](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/dbt_project/models/silver/schema.yml), [Gold](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/dbt_project/models/gold/schema.yml)) para restrições de chave única, não-nulos e valores aceitos.

### 5. Orquestração e Feedback Loops (Apache Airflow)
*   [btc_ingestion_and_transform.py](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/dags/btc_ingestion_and_transform.py): Executa de 5 em 5 minutos a ingestão pontual, dbt run e dbt test.
*   [btc_backfill.py](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/dags/btc_backfill.py): DAG de carregamento histórico parametrizada executada sob demanda.
*   [src/ingestion/gap_detector.py](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/src/ingestion/gap_detector.py) e [btc_auto_recovery.py](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/dags/btc_auto_recovery.py): DAG horária de monitoramento que varre o banco em busca de gaps de dados e executa automaticamente a ingestão histórica corretiva para preencher lacunas (loop de retroalimentação).

### 6. Visualização e Auditoria (Streamlit)
*   [src/app/dashboard.py](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/src/app/dashboard.py): Dashboard premium com tema escuro e visual limpo contendo:
    *   Métricas agregadas em tempo real com deltas.
    *   Gráficos Plotly interativos dos preços e taxa de câmbio USD/BRL implícita.
    *   Comparador de granularidades analíticas da camada Gold.
    *   Página de Auditoria e Status contendo logs de execução da pipeline e relatórios de quarentena.

---

## 🛠️ Guia de Inicialização Rápida no Terminal

1.  Acesse a pasta raiz do projeto.
2.  Copie o `.env.example` para `.env` e configure se desejar:
    ```bash
    cp .env.example .env
    ```
3.  Construa e inicie os containers:
    ```bash
    docker compose up -d --build
    ```
4.  Acesse o painel Streamlit em [http://localhost:8501](http://localhost:8501) e execute o **Backfill manual** para popular os dados e rodar o dbt pela primeira vez.
5.  Acesse a UI do Airflow em [http://localhost:8080](http://localhost:8080) (usuário `admin` / senha `admin`) para visualizar os fluxos de DAG agendados e executados.
