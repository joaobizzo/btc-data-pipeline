# Roteiro de Apresentação: Prova 2 - BTC Data Pipeline

Este guia foi elaborado com base nos critérios de avaliação da **2ª Avaliação (Menção Parcial 2)** para ajudá-los a conduzir uma apresentação fluida, técnica e segura perante o professor, dividindo de forma clara as falas e demonstrações de cada integrante.

---

## Divisão de Falas e Tempo (Total: ~10 a 12 minutos)

| Tópico | Duração | Apresentador Principal | O que Fazer / Mostrar |
| :--- | :---: | :---: | :--- |
| **1. Introdução e Domínios** | 2 min | **João** | Contextualização do negócio e novos domínios. |
| **2. Arquitetura "As-Built"** | 3 min | **Pietra** | Explicação técnica do diagrama e caminhos não-felizes. |
| **3. Demonstração: BD e Airflow** | 3 min | **João** | Mostrar schemas Postgres e disparar DAG de Backfill. |
| **4. Demonstração: Streamlit** | 2 min | **Pietra** | Mostrar gráficos, granularidades Gold e quarentena. |
| **5. Defesa e Perguntas (Q&A)** | 2 min | **Ambos** | Responder às arguições técnicas do professor. |

---

## 1. Introdução e Domínios de Negócio (Apresentador: João)
*   **Abertura:** Apresente a equipe (João e Pietra) e o nome do projeto: *BTC Data Pipeline – Monitoramento Inteligente de Preços de Bitcoin*.
*   **O Problema de Negócio:** Investidores precisam de dados históricos longos (para análises de tendência) mas também dados recentes de alta resolução. Salvar tudo com alta frequência estouraria o armazenamento. A solução é coletar dados em tempo real e aplicar agregações de série temporal (*downsampling*).
*   **A Evolução dos Domínios (Feedback da Prova 1):** Explique que na P1 os domínios eram apenas etapas do pipeline. Agora, reestruturamos de acordo com **domínios de conhecimento de negócio**:
    1.  *Inteligência de Mercado Cripto:* Lida com a API CoinGecko e garante a ingestão Bronze.
    2.  *Conversão Cambial:* Calcula o câmbio implícito BRL/USD usando a paridade de mercado do Bitcoin, sem depender de APIs de moedas externas.
    3.  *Métricas e Analytics Temporal:* Aplica qualidade de dados, quarentena e agregações.
    4.  *Portfólio e Consumo:* Serve os dados para as interfaces visuais.

---

## 2. Arquitetura "As-Built" e Resiliência (Apresentadora: Pietra)
*   **Exibição do Diagrama:** Abra o README.md na seção do diagrama Mermaid e explique o fluxo:
    *   **Ingestão & Qualidade:** Os coletores Python gravam no schema `bronze` (`raw_realtime` e `raw_historical`). Se falhar na qualidade (preço negativo, nulos), vai para a tabela `quarantine`.
    *   **Normalização & Agregação:** O dbt limpa, calcula o câmbio implícito e grava na tabela `silver.silver_prices`. Em seguida, cria as visões da camada `gold` agrupadas em 2h, 4h e Diária.
*   **Caminho Não-Feliz e Retroalimentações:**
    1.  *Tenacity (Exponential Backoff):* Tratamento contra rate-limit (HTTP 429) no cliente Python.
    2.  *Gap Detector (Autocura):* O script `gap_detector.py` monitora o banco em busca de lacunas na série temporal. Ao detectar um gap maior que 4 horas, ele dispara automaticamente a DAG de Backfill Histórico para recuperar os dados perdidos.

> **Sugestão de Fala para a Pietra:**
> *"Professor, no planejamento inicial focamos no 'caminho feliz'. Na implementação, nossa prioridade foi a governança e a tolerância a falhas. Implementamos um fluxo em que os dados brutos passam por um validador de regras de qualidade em Python antes de entrarem na tabela Silver. Se um registro contiver um preço nulo ou negativo, ele é automaticamente isolado na tabela de Quarentena com um log explicativo, evitando poluir nossas médias e mantendo a integridade analítica."*
>
> **Explicação Técnica do Loop de Autocura (Pietra):**
> *"Para lidar com a instabilidade da API ou quedas de internet local, criamos um mecanismo de retroalimentação ativa (feedback loop). A DAG `btc_auto_recovery` executa de hora em hora o script `gap_detector.py`. Esse script roda uma query SQL analítica na camada Silver medindo o intervalo entre os timestamps consecutivos (`LEAD(price_timestamp) OVER (...)`). Caso seja identificado um gap de tempo superior a 4 horas, o script dispara automaticamente o processo de Backfill do período exato da lacuna, auto-curando nossa base de dados histórica sem necessidade de manutenção manual."*

---

## 3. Demonstração Prática: BD e Orquestração (Apresentador: João)

*   **A. O Banco de Dados (PostgreSQL):**
    *   *O que abrir:* DBeaver, pgAdmin ou terminal.
    *   *O que mostrar:* Mostre os quatro schemas estruturados no banco `btc_pipeline`: `bronze`, `silver`, `gold` e `monitoring`. Aponte a tabela `bronze.quarantine` como exemplo de governança e isolamento de dados ruins.
*   **B. A Orquestração (Apache Airflow):**
    *   *O que abrir:* Navegador em http://localhost:8080 (usuário `admin` / senha `admin`).
    *   *O que mostrar:*
        1.  DAG `btc_ingestion_and_transform` (coleta realtime + dbt run/test a cada 5 min).
        2.  DAG `btc_auto_recovery` (verificador de gaps horários).
        3.  DAG `btc_historical_backfill` (backfill manual). **Clique em "Trigger DAG" em tempo real** para o professor ver os containers rodando o `dbt run` com sucesso.

---

## 4. Demonstração Prática: Dashboard (Apresentadora: Pietra)

*   *O que abrir:* Navegador em http://localhost:8501.
*   *O que mostrar:*
    *   **Aba 1 (Cotações):** Mostre as cotações em USD e BRL e o cálculo do dólar implícito gerado a partir do Bitcoin. Mostre que os gráficos Plotly são interativos.
    *   **Aba 2 (Granularidades Gold):** Mostre os dados da Gold agrupados em 2h, 4h ou diário. Explique a faixa cinza de volatilidade (Preço Médio, Máximo e Mínimo).
    *   **Aba 3 (Monitoramento e Qualidade):** Mostre os logs operacionais da tabela `monitoring.pipeline_logs` provando o registro das tarefas e a tabela da Quarentena zerada (ou com registros, se simulou erro).

> **Sugestão de Fala para a Pietra:**
> *"Nesta tela do Streamlit, podemos visualizar a entrega de valor final. A aba de Cotações calcula dinamicamente a taxa cambial implícita BRL/USD dividindo o preço do Bitcoin em BRL pelo seu preço em USD de forma instantânea. Na aba de Granularidades (Gold), o usuário consome visões agregadas de 2 horas, 4 horas e Diário. Projetamos a área sombreada usando Plotly para exibir o envelope de volatilidade (o preço máximo e mínimo atingidos dentro de cada período em relação à média). Isso resolve a questão de performance de leitura de grandes volumes de séries temporais."*
>
> **Explicando a Aba de Monitoramento (Pietra):**
> *"Finalmente, na aba de Monitoramento e Qualidade, expomos a governança e transparência do pipeline. Ela lê o schema `monitoring` do Postgres, mostrando a taxa de sucesso das DAGs de orquestração do Airflow e a listagem em tempo real da tabela de Quarentena de Qualidade, permitindo que o gestor de dados audite e trace falhas de payloads brutos instantaneamente."*

---

## 5. Defesa e Perguntas Frequentes (Ambos)

Esteja preparado para dividir a defesa se o professor arguir:

*   **P: Por que usar o Streamlit em vez do Metabase (planejado na Prova 1)? (Defesa: Pietra)**
    *   *Resposta:* O Metabase exige a criação e configuração manual de painéis em runtime, o que dificulta o versionamento do layout do dashboard no Git. Com o Streamlit, toda a aplicação, gráficos e consultas SQL são codificados em Python, permitindo que a interface seja 100% versionada e transportada de forma transparente entre máquinas (portabilidade).
*   **P: Por que usar dbt em vez de scripts Python/Pandas convencionais? (Defesa: João)**
    *   *Resposta:* O dbt realiza o processamento diretamente dentro do banco de dados (ELT), otimizando performance. Ele também gerencia DDLs e chaves automaticamente, oferece testes nativos (`dbt test`) para restrições de qualidade de dados e documenta a linhagem dos dados de forma automatizada.
*   **P: Como o pipeline reage se a máquina host perder internet? (Defesa: Pietra)**
    *   *Resposta:* O script de ingestão tentará reconectar com backoff exponencial. Se o tempo for longo, a tarefa falhará. Ao retornar a conexão, a DAG `btc_auto_recovery` detectará o buraco temporal na tabela `silver.silver_prices` na sua execução seguinte e disparará o backfill do intervalo exato da falha, auto-curando o banco.
