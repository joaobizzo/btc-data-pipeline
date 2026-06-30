# 🪙 Roteiro de Apresentação: Prova 2 - BTC Data Pipeline

Este guia foi elaborado com base nos critérios de avaliação da **2ª Avaliação (Menção Parcial 2)** para ajudá-lo a conduzir uma apresentação fluida, técnica e segura perante o professor. Ele descreve o que falar, o que mostrar e como defender as decisões de engenharia adotadas.

---

## ⏱️ Divisão do Tempo Sugerida (Total: ~10 a 12 minutos)

1.  **Introdução e Domínios de Negócio** (2 minutos)
2.  **Arquitetura "As-Built" e Evolução (Feedbacks Prova 1)** (3 minutos)
3.  **Demonstração Prática do Pipeline e dos Containers** (5 minutos)
4.  **Conclusão e Defesa das Escolhas Técnicas** (2 minutos)

---

## 1. Introdução e Domínios de Negócio (O quê e Porquê)
*   **Abertura:** Apresente-se (João Bizzo e Pietra Paz) e apresente o projeto: *BTC Data Pipeline – Monitoramento Inteligente de Preços de Bitcoin*.
*   **O Problema de Negócio:** Investidores de criptoativos precisam balancear a visualização de dados históricos de longo prazo com alta resolução recente para tomar decisões de compra/venda. Porém, armazenar tudo em alta frequência gera custos excessivos.
*   **Solução:** Um pipeline em camadas lógicas (Medalhão) que faz o *downsampling* (agregação temporal) inteligente de preços do Bitcoin (coletados via CoinGecko) e calcula taxas de câmbio implícitas.
*   **Correção de Domínios (Feedback P1):** Explique ao professor que na Prova 1 os domínios estavam acoplados às etapas do pipeline. Agora, foram organizados por **domínios de negócio/conhecimento**:
    1.  *Inteligência de Mercado Cripto* (coleta, resiliência na API e auditoria Bronze);
    2.  *Conversão Cambial* (cálculo de câmbio implícito BRL/USD sem dependência de APIs externas);
    3.  *Métricas e Analytics Temporal* (validação de qualidade, agregação e autocura);
    4.  *Portfólio e Consumo* (dashboard analítico Streamlit).

---

## 2. Arquitetura "As-Built" e Evolução (Como foi feito)
*   **Abra o [README.md](file:///home/joaobizzo/Documents/CEUB/8sem/eng%20Dados/btc-data-pipeline/README.md)** e mostre o diagrama Mermaid atualizado.
*   **Explique o Fluxo de Dados Ponta a Ponta:**
    *   **Ingestão (Bronze):** Coleta em Python (Requests) e persistência do JSON bruto nas tabelas `raw_realtime` e `raw_historical`.
    *   **Qualidade e Quarentena:** Antes da inserção, os dados passam por uma barreira de qualidade em Python. Dados corrompidos (ex: preços negativos ou nulos) são desviados para a tabela `quarantine`.
    *   **Normalização (Silver):** O dbt limpa o JSON, padroniza os timestamps para UTC, calcula a taxa de câmbio implícita e grava em `silver.normalized_prices`.
    *   **Agregações (Gold):** O dbt gera agregações em janelas temporais de **2h**, **4h** e **Diário** (tabelas da camada Gold).
    *   **Consumo (Serving):** Dashboard Streamlit interativo e logs de auditoria expostos ao usuário.
*   **Destaque os Mecanismos de Retroalimentação (Caminho não-feliz):**
    1.  *Resiliência de API:* Uso de *exponential backoff* (via biblioteca `tenacity`) para contornar bloqueios por rate limit (HTTP 429).
    2.  *Loop de Autocura (Gap Detector):* O script `gap_detector.py` monitora o banco em busca de lacunas na série temporal. Ao detectar um gap maior que 4 horas, ele dispara automaticamente a DAG de Backfill Histórico para recuperar os dados perdidos.

---

## 3. Demonstração Prática (O que abrir e mostrar na tela)

Para obter a nota máxima em **Funcionalidade e Operacionalidade**, abra os seguintes serviços locais na hora da apresentação:

### A. O Banco de Dados (PostgreSQL)
*   *Onde abrir:* Um cliente SQL de sua preferência (ex: DBeaver, pgAdmin) ou via linha de comando no container.
*   *O que mostrar:*
    *   Os quatro schemas estruturados no banco `btc_pipeline`: `bronze`, `silver`, `gold` e `monitoring`.
    *   Destaque a tabela `bronze.quarantine` e comente: *"Se a CoinGecko enviar um dado inválido, ele não quebra o dashboard, ele é isolado aqui para governança."*

### B. A Orquestração (Apache Airflow)
*   *Onde abrir:* Navegador em [http://localhost:8080](http://localhost:8080) (usuário `admin` / senha `admin`).
*   *O que mostrar:*
    *   As 3 DAGs ativas e configuradas em código:
        1.  `btc_ingestion_and_transform`: Mostre que ela roda a cada 5 minutos, captura o dado brut, aciona o `dbt run` e executa o `dbt test` para validar o schema.
        2.  `btc_historical_backfill`: DAG manual. Clique em *Trigger DAG* para mostrar ao professor uma carga histórica em lote rodando em tempo real.
        3.  `btc_auto_recovery`: Mostre o código ou gráfico explicativo do detector de gaps (loop de retroalimentação horária).

### C. A Interface de Consumo e Monitoramento (Streamlit)
*   *Onde abrir:* Navegador em [http://localhost:8501](http://localhost:8501).
*   *O que mostrar:*
    *   **Aba 1 (Cotações):** Mostre as cotações em USD e BRL e o cálculo do dólar implícito gerado a partir do Bitcoin. Mostre que os gráficos Plotly são interativos.
    *   **Aba 2 (Granularidades Gold):** Mostre os dados consolidados de 2h, 4h e diários. Aponte a área sombreada do gráfico que ilustra a volatilidade (Preço Médio vs Máximo e Mínimo).
    *   **Aba 3 (Monitoramento e Qualidade):** Mostre as métricas executivas de saúde da pipeline (quantidade de execuções de sucesso/falha) e a listagem em tempo real da tabela `pipeline_logs` e `quarantine`.

---

## 4. Defesa e Perguntas Frequentes (Perguntas que o professor pode fazer)

*   **P: Por que usar o Streamlit em vez do Metabase (que estava no planejamento original)?**
    *   *Defesa:* O Metabase exige a criação e configuração manual de painéis em runtime, o que dificulta o versionamento do layout do dashboard no Git. Com o Streamlit, toda a aplicação, gráficos e consultas SQL são codificados em Python, permitindo que a interface seja 100% versionada e transportada de forma transparente entre máquinas (portabilidade).
*   **P: Por que usar dbt se poderíamos fazer tudo em Pandas/Python?**
    *   *Defesa:* O dbt padroniza o processamento SQL dentro da própria base de dados (ELT), otimizando a performance. Além disso, ele gerencia automaticamente a DDL (não precisamos escrever `CREATE TABLE` manuais) e provê testes integrados de qualidade de dados (`dbt test`) e documentação de linhagem sem esforço adicional.
*   **P: O que acontece se a internet cair durante a execução de 5 minutos?**
    *   *Defesa:* O script de ingestão possui retentativas com backoff exponencial. Se a queda for prolongada, a DAG falhará e registrará o status `FAILURE` na tabela de logs de monitoramento. Quando a conexão retornar, o detector de lacunas (`btc_auto_recovery`) identificará o gap na série temporal na próxima execução e disparará o backfill automático do período faltante, restabelecendo a consistência histórica sem intervenção manual.
