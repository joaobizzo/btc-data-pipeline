# 🚀 Tutorial de Execução: BTC Data Pipeline

Este tutorial guia você na inicialização do ambiente Docker e no carregamento inicial dos dados para garantir que sua apresentação ao professor mostre o pipeline funcionando com dados reais.

---

## ❓ Preciso povoar dados para apresentar?
**Sim, com certeza!** Sem dados inseridos, o banco de dados estará vazio e o dashboard no Streamlit exibirá mensagens de aviso informando que as tabelas não possuem registros.

Para apresentar o projeto com sucesso, você precisa realizar a **Carga Inicial (Bootstrap)**. Isso coletará o histórico recente do CoinGecko e executará o dbt para transformar e consolidar as camadas Silver e Gold, deixando os gráficos populados e prontos.

---

## 🛠️ Passo a Passo para Rodar o Projeto

### Passo 1: Preparar as Variáveis de Ambiente
Na raiz do repositório, copie o arquivo `.env.example` para `.env`:
```bash
cp .env.example .env
```
*(Nota: O `.env` já vem pré-configurado com credenciais do banco e uma chave Fernet do Airflow válida).*

### Passo 2: Subir os Containers Docker
Execute o comando abaixo para construir as imagens customizadas (com dbt e bibliotecas Python) e iniciar os serviços em segundo plano:
```bash
# Caso utilize Docker Compose V2 (Recomendado):
docker compose up -d --build

# Caso utilize Docker Compose V1 (antigo):
docker-compose up -d --build
```

### Passo 3: Aguardar a Inicialização do Airflow
O container `btc_airflow_init` criará a estrutura de metadados do Airflow e o usuário padrão. Isso leva de 1 a 2 minutos. 
Verifique se todos os containers estão saudáveis executando:
```bash
docker compose ps
```
Você verá os containers `btc_postgres`, `btc_streamlit`, `btc_airflow_webserver` e `btc_airflow_scheduler` com o status `running` (ou `healthy`).

---

## ⚡ Passo 4: Como Alimentar os Dados (Bootstrap)

Escolha **uma** das opções abaixo para encher seu banco de dados com dados de mercado reais:

### Opção A: Pelo Streamlit (Mais Rápida e Fácil)
1.  Abra o navegador em [http://localhost:8501](http://localhost:8501).
2.  Como o banco estará vazio, o painel exibirá uma mensagem de erro amigável.
3.  Clique no botão **"Executar Ingestão Histórica de 7 dias agora"** disponível no aviso.
4.  O sistema se conectará à API, inserirá os dados brutos e rodará as transformações dbt automaticamente. Ao terminar, o dashboard se atualizará sozinho com todos os gráficos!

### Opção B: Pelo Airflow (Recomendado para impressionar o professor)
1.  Abra o navegador em [http://localhost:8080](http://localhost:8080).
2.  Faça login com: **Usuário:** `admin` | **Senha:** `admin`
3.  Ative a DAG clicando na chave liga/desliga ao lado esquerdo de `btc_historical_backfill` (deixando-a azul).
4.  Clique no botão **Play (Trigger DAG)** no canto direito da linha para disparar.
5.  Acompanhe a execução das caixas: ela coletará os últimos 30 dias de dados, rodará as tabelas Silver/Gold no dbt e executará os testes de qualidade automáticos.

---

## 🔍 Passo 5: Verificações e Testes

Durante a apresentação, você pode abrir os seguintes endereços para provar que o ciclo de vida está operacional:

1.  **Orquestrador (Airflow):** [http://localhost:8080](http://localhost:8080)
    *   Mostre as DAGs agendadas e os logs de execução.
2.  **Consumo e Monitoramento (Streamlit):** [http://localhost:8501](http://localhost:8501)
    *   Interaja com os gráficos e exiba os logs de execução na aba "Monitoramento e Qualidade".
3.  **Tabelas de Banco (Postgres):**
    *   Se o professor pedir para ver o banco, use o DBeaver ou conecte via terminal:
        ```bash
        docker exec -it btc_postgres psql -U postgres -d btc_pipeline
        ```
    *   Para ver os dados estruturados pelo dbt:
        ```sql
        SELECT * FROM silver.normalized_prices LIMIT 10;
        SELECT * FROM gold.prices_aggregated_2h LIMIT 10;
        ```
