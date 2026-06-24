# Plano de Implementação: Prova 2 - BTC Data Pipeline

Este documento apresenta o plano detalhado para a implementação e refinamento do protótipo do ciclo de vida de engenharia de dados para o monitoramento inteligente de preços do Bitcoin. Ele aborda os requisitos da Prova 2 e corrige as lacunas identificadas no feedback da Prova 1 (nota_prova1.txt).

---

## User Review Required

> [!IMPORTANT]
> **Ajustes de Arquitetura e Feedback da Prova 1**
> O feedback da Prova 1 apontou que:
> 1. Os domínios devem refletir áreas de negócio/conhecimento (ex: Inteligência de Mercado Cripto, Análise Macroeconômica de Câmbio, Portfólio de Investimentos) e não etapas técnicas do pipeline.
> 2. Faltou monitoramento, governança, qualidade de dados e fluxos de retroalimentação (caminho não-feliz).
> 3. Faltou justificar as escolhas de tecnologias e detalhar as de monitoramento, governança e qualidade.
>
> Proponho corrigirmos isso na arquitetura prática e nos documentos do projeto.

> [!NOTE]
> **Abordagem de Orquestração Leve**
> Apache Airflow pode ser pesado para execução local em computadores pessoais de estudantes (consome 2GB+ RAM). Proponho uma alternativa usando um orquestrador leve em Python (como o framework `Prefect` ou uma solução modular via `APScheduler` rodando em container), mas mantendo a opção do `Apache Airflow` leve (usando o `puckel/docker-airflow` ou similar) caso seja uma exigência rigorosa da disciplina.
>
> **Consumo / Serving**
> Proponho o uso de **Streamlit** (em Python) para construir a interface de consumo e monitoramento. Ele é leve, de fácil desenvolvimento, e seu código fica salvo no repositório Git, facilitando a entrega.

---

## Open Questions

> [!IMPORTANT]
> 1. **Preferência de Orquestrador:** O grupo prefere tentar rodar o **Apache Airflow** (com imagem Docker leve) ou prefere usar uma abordagem mais leve em Python puro/APScheduler/Prefect para economizar recursos de máquina?
> 2. **Ferramenta de Visualização:** Streamlit é altamente recomendado por ser codificado em Python e facilmente versionável no Git. Podemos seguir com ele ou há preferência por Metabase (que exige subir outro container e configurar os dashboards manualmente em runtime)?
> 3. **Configuração do dbt:** Para as transformações da camada Silver/Gold, deseja usar **dbt-postgres** ou prefere scripts Python puramente utilizando **Pandas / SQLAlchemy**? O dbt traz boas práticas de mercado, documentação e testes integrados, enquanto Pandas é mais direto.

---

## Proposed Changes

Abaixo está a estrutura proposta para o repositório atualizado:

```
btc-data-pipeline/
├── Dockerfile.ingestion     # Dockerfile para o container de ingestão e orquestração
├── Dockerfile.streamlit     # Dockerfile para a aplicação de dashboard (Streamlit)
├── docker-compose.yml       # Orquestração local (Postgres, Ingestion, Dashboard)
├── requirements.txt         # Dependências do projeto (requests, pandas, psycopg2, streamlit, etc.)
├── .env.example             # Modelo de variáveis de ambiente (credenciais de banco, chaves se houver)
├── .gitignore               # Ignorar .env, __pycache__, logs locais, etc.
├── README.md                # Documentação principal atualizada com arquitetura "As-Built"
├── docs/                    # Documentação do projeto (atualizada)
│   ├── 01_descricao_projeto.md
│   ├── 02_dados.md
│   ├── 03_dominios.md       # Atualizado com novos domínios de negócio e governança
│   ├── 04_arquitetura.md    # Atualizado com fluxo completo (incluindo qualidade, monitoramento e retroalimentação)
│   ├── 05_tecnologias.md    # Atualizado com justificativas e ferramentas de governança/qualidade
│   └── 06_consideracoes.md
├── src/                     # Código-fonte da implementação
│   ├── __init__.py
│   ├── config.py            # Configurações globais e carregamento de variáveis .env
│   ├── database.py          # Utilitários de conexão e criação de tabelas (Postgres)
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── client.py        # Cliente HTTP CoinGecko (resiliência com retentativas, rate limit e tratamentos de erro)
│   │   └── pipeline.py      # Execução de coleta Realtime (Bronze) e Backfill (Bronze)
│   ├── transformation/
│   │   ├── __init__.py
│   │   └── dbt_or_pandas.py # Scripts de processamento (Silver e Gold - agregações, normalização, câmbio implícito)
│   ├── quality/
│   │   ├── __init__.py
│   │   └── rules.py         # Regras de qualidade de dados (verificar nulos, preços negativos, etc.)
│   ├── scheduler/
│   │   ├── __init__.py
│   │   └── main.py          # Orquestrador leve que coordena o fluxo de execução e trata erros
│   └── app/
│       ├── __init__.py
│       └── dashboard.py     # Painel de visualização (Streamlit) e tela de monitoramento de status da pipeline
```

---

### Componentes de Implementação

#### 1. Banco de Dados (Armazenamento)
- Subiremos um banco **PostgreSQL** via `docker-compose.yml`.
- Criaremos esquemas lógicos para representar as camadas:
  - `bronze`: dados crus JSON como strings/JSONB diretamente da API (`raw_realtime` e `raw_historical`).
  - `silver`: dados normalizados, com tipos corretos, campos padronizados e cálculo de câmbio implícito (`normalized_prices`).
  - `gold`: dados agregados por granularidade (tabela `prices_aggregated_2h`, `prices_aggregated_4h`, `prices_aggregated_daily`).
  - `monitoring`: tabela `pipeline_logs` para registrar data, status, registros processados, erros e métricas de qualidade.

#### 2. Ingestão (Bronze)
- Um script Python robusto em `src/ingestion/` que consome a API CoinGecko.
- **Resiliência e Retroalimentação (Caminho não-feliz):**
  - Se a chamada da API falhar (ex: rate limit 429 ou timeout), o script usará *exponential backoff* para retentar.
  - Se falhar consecutivamente, registrará um erro crítico no banco e enviará uma sinalização de alerta (log do sistema).
  - O serviço de Backfill detectará lacunas na tabela `silver.normalized_prices` e acionará automaticamente a coleta histórica batch para preencher o gap.

#### 3. Qualidade de Dados (Data Quality)
- Regras executadas na transição Bronze -> Silver:
  - Garantia de não-nulos em campos chave (preço, timestamp).
  - Verificação se o preço é estritamente positivo (> 0).
  - Verificação de duplicatas (combinação única de timestamp e fonte).
  - Registros com falha de qualidade são desviados para uma tabela de rejeitados/quarentena (`bronze.quarantine`) para auditoria e governança (retroalimentação), evitando poluir o dashboard.

#### 4. Transformação (Silver/Gold)
- Processamento que extrai o JSON da camada Bronze, valida com as regras de qualidade, e insere na camada Silver.
- Aplica o cálculo do câmbio implícito `usd_brl = price_brl / price_usd`.
- Agrega em lote para a camada Gold nas janelas temporais de 2h, 4h e Diária.

#### 5. Orquestração e Monitoramento
- Um container leve de orquestração rodando um scheduler Python (ex: `APScheduler`). Ele agenda:
  - A execução de 5 em 5 minutos da ingestão (para simular e validar o fluxo em tempo real rapidamente).
  - A execução diária ou em intervalos regulares do backfill/sincronização.
- O monitoramento gravará cada etapa na tabela `monitoring.pipeline_logs`.

#### 6. Dashboard de Consumo e Monitoramento (Streamlit)
- Uma interface visual premium contendo:
  - Gráficos interativos do preço do Bitcoin em USD e BRL e a taxa de câmbio implícita calculada.
  - Tabelas de comparação de dados em diferentes granularidades (2h, 4h, Diário).
  - **Página de Monitoramento/Qualidade:** Exibição da saúde da pipeline (última execução, status de sucesso/falha, número de registros validados na camada de Qualidade, registros em quarentena).

---

## Planos para os Próximos Passos (Após Aprovação)

1. **Definir e reestruturar os documentos da Prova 1** (`docs/03_dominios.md`, `docs/04_arquitetura.md` e `docs/05_tecnologias.md`) para atender aos feedbacks recebidos do professor.
2. **Escrever a infraestrutura Docker** (`docker-compose.yml` e `Dockerfiles`).
3. **Desenvolver o código base de banco e ingestão** (`database.py`, `client.py` e `pipeline.py`).
4. **Implementar a camada de Qualidade de Dados, Transformações e Quarentena**.
5. **Implementar a orquestração e logging de monitoramento**.
6. **Desenvolver a interface Streamlit**.
7. **Verificar e documentar o projeto "As-Built" no README.md**.

---

## Verification Plan

### Automated Tests
- Testar conectividade e lógica de banco de dados rodando scripts locais/de teste.
- Executar validações de qualidade de dados com inputs simulados (ex: preço negativo, nulos) para garantir que caem na quarentena.

### Manual Verification
- Iniciar o `docker-compose up --build`.
- Acessar o dashboard Streamlit em `http://localhost:8501`.
- Simular uma falha (ex: desativar a rede ou colocar chaves inválidas) e verificar se o erro é corretamente monitorado e exibido na aba de logs de monitoramento.
- Verificar no Postgres se as tabelas nas três camadas (Bronze, Silver, Gold) foram criadas e populadas corretamente.
