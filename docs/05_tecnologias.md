# 🛠️ Justificativa e Seleção das Tecnologias

A escolha das tecnologias para a implementação do **BTC Data Pipeline** baseou-se em critérios de robustez, adoção de mercado, capacidade de execução local em ambientes de desenvolvimento (notebooks) e suporte nativo às boas práticas de Engenharia de Dados.

---

## 1. Tecnologias Principais do Pipeline

### Ingestão: Python + Requests + Tenacity
*   **Justificativa:** Python é a linguagem padrão em Engenharia de Dados. A biblioteca `requests` fornece controle direto e de baixo nível sobre os cabeçalhos HTTP, essencial para tratar chamadas à API da CoinGecko. Usamos a biblioteca de resiliência `tenacity` em Python para automatizar a lógica de retentativas e *exponential backoff* quando a API retornar rate limit (código 429) ou timeouts de conexão.

### Armazenamento: PostgreSQL (rodando em Docker)
*   **Justificativa:** Banco de dados relacional maduro, confiável e compatível com ACID. Suporta tipos de dados como `JSONB` na camada Bronze (armazenamento flexível e auditável do payload bruto) e tabelas relacionais indexadas por chaves e timestamps nas camadas Silver e Gold (séries temporais otimizadas). Roda de forma isolada em um container leve do Docker, facilitando a portabilidade do projeto.

### Orquestração: Apache Airflow (Dockerizado)
*   **Justificativa:** É a ferramenta líder de mercado em orquestração de pipelines de dados. Permite a definição de fluxos como DAGs (Directed Acyclic Graphs) em código Python, agendando de forma determinística a coleta contínua (5 min) e os processos dbt. Suporta nativamente:
    *   **Backfill:** Execução retroativa histórica inteligente.
    *   **Políticas de Retentativa:** Mecanismo integrado de retry caso as tarefas falhem.
    *   **Lightweight Container:** Ajustado para rodar de forma otimizada no Docker com recursos limitados de RAM (notebook do estudante).

### Processamento e Transformação: dbt (Data Build Tool - dbt-postgres)
*   **Justificativa:** O dbt é o padrão de mercado para transformações na camada de armazenamento (T do ELT). Ele nos permite escrever transformações complexas (de Bronze para Silver e Silver para Gold) em SQL estruturado, automatizando a criação de views e tabelas incrementais sem a necessidade de gerenciar comandos DDL (`CREATE TABLE`, `INSERT`, etc.) manualmente.

### Consumo / Serving: Streamlit
*   **Justificativa:** Framework de código aberto em Python para desenvolvimento rápido de aplicações web ricas de dados. A principal vantagem é que todo o layout e lógica de gráficos é codificado em arquivos Python, permitindo versionamento total no repositório Git (diferente de ferramentas como Metabase ou Power BI, cujos dashboards criados em tela não são facilmente versionáveis em código aberto e limpo).

---

## 2. Tecnologias de Correntes do Ciclo de Vida

```
┌────────────────────────────────────────────────────────┐
│               QUALIDADE DE DADOS                       │
│ - dbt tests (Unique, Not Null, Accepted Values)        │
│ - Script Python de Validação Pré-Bronze                │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│                 MONITORAMENTO                          │
│ - Postgres Table (monitoring.pipeline_logs)            │
│ - Airflow Scheduler UI & logs de execução              │
│ - Streamlit Dashboard de Status (Visão Executiva)      │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│                   GOVERNANÇA                           │
│ - dbt docs (Linhagem de dados e Metadados)             │
│ - Schema isolation (Bronze / Silver / Gold)            │
│ - .env para Segurança de Credenciais                   │
└────────────────────────────────────────────────────────┘
```

### Qualidade de Dados (Data Quality)
*   **Validação Pré-Bronze:** Script Python executa validação de formato e tipo de dados antes de salvar na camada Raw.
*   **dbt Tests:** O dbt executa asserções na camada Silver e Gold. Configura-se testes de integridade referencial, restrições de unicidade de chave (timestamp único), não nulos e validações lógicas (preços e câmbios maiores que zero). Registros com erro são desviados para uma tabela de quarentena.

### Monitoramento
*   **Log Table (`monitoring.pipeline_logs`):** Tabela relacional dedicada que armazena os metadados de cada tarefa rodada (horário, registros processados, erros ocorridos).
*   **Logs do Airflow:** Utilizados para rastreabilidade de código a nível de container.
*   **Visão Executiva:** Uma página dedicada no painel do Streamlit consome os metadados da tabela de logs do Postgres para apresentar em formato visual se o pipeline está operando de forma saudável.

### Governança e Linhagem
*   **dbt Docs & Lineage:** O dbt gera documentação automatizada (um portal estático HTML) contendo a linhagem completa dos dados (lineage graph), rastreando a origem de cada métrica desde o JSON bruto até a agregação de consumo Gold, facilitando auditoria e entendimento de metadados.
*   **Segurança (Credenciais):** Uso obrigatório do pacote `python-dotenv` para ler chaves e credenciais do banco a partir de um arquivo `.env` local, mantendo segredos fora do repositório Git.
