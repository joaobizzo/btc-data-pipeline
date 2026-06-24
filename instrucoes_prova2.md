## 2ª Avaliação: Implementação e Refinamento do Protótipo (Menção Parcial 2)

### 1\. Objetivo

O objetivo desta segunda etapa é tirar o projeto do papel. Vocês deverão **implementar** o ciclo de vida de engenharia de dados que foi planejado na primeira avaliação, realizando as adaptações necessárias para que o protótipo seja funcional e executável.

### 2\. Equipe e Detalhes

-   Até 3 pessoas.
-   As horas finais de cada aula até o dia da apresentação serão dedicadas à mentoria técnica dos projetos. Dada a complexidade da implementação, essa é uma oportunidade para validarmos a arquitetura e sanarmos gargalos antes da avaliação.

### 3\. O que deve ser entregue (Repositório GitHub)

O repositório do grupo deve ser atualizado para refletir o trabalho prático. A avaliação será dividida em dois grandes blocos:

#### a. Implementação Prática (8,0 pontos)

A nota será atribuída com base na existência e funcionamento dos seguintes itens no repositório:

-   **Código de Ingestão:** Scripts ou configurações que realizam a extração dos dados da fonte e carga inicial.
-   **Armazenamento:** Configuração do banco de dados ou estrutura de pastas do Data Lake (uso de Docker é recomendado).
-   **Transformação:** Código que realiza a limpeza, normalização ou agregação dos dados (ex: dbt, Spark, scripts Python).
-   **Orquestração:** Demonstração de como as tarefas são agendadas ou encadeadas (ex: Airflow, Prefect ou um script).
-   **Consumo (Serving):** Uma interface mínima ou query final que demonstre o dado pronto para uso (ex: dashboard em Streamlit, Metabase, Power BI ou uma API).

#### b. Atualização da Arquitetura "As-Built" (2,0 pontos)

Dificilmente o que foi planejado é executado sem alterações. Vocês devem:

-   **Atualizar o Diagrama de Arquitetura:** Utilizando Mermaid ou outra ferramenta, apresentem o diagrama final do que foi **efetivamente implementado**.
-   **Relatório de Mudanças:** Um breve texto (no README.md) explicando o que mudou em relação ao plano original e as justificativas técnicas para essas mudanças (ex: troca de uma ferramenta por limitações de hardware).

### 4\. Formato de Entrega

1.  **Documento (atenção ao prazo na atividade aqui no Sala Online):** link e print do repositório e observações que queira encaminhar.
2.  **Apresentação:** em sala no dia 25/06 (caso não haja tempo para as apresentações, poderá ser usado o dia 02/07).

### 5\. Critérios de Avaliação

-   **Atenção:** Para a composição da nota, é indispensável tanto o envio do documento via Sala Online quanto a apresentação em sala de aula. **O não cumprimento de ambas as etapas implicará em menção SR para a equipe.**

#### **a. Funcionalidade e Operacionalidade (6,0 pontos)**

O foco aqui é a execução do ciclo de vida ponta a ponta. O protótipo será avaliado pela capacidade de manter o dado fluindo com integridade:

-   **Pipeline:** Execução funcional das etapas de **Ingestão, Armazenamento e Transformação**.
-   **Entrega de Valor:** Disponibilização dos dados para **Consumo** (Dashboards, APIs ou consultas estruturadas).
-   **Ciclo:** Implementação de camadas de **Qualidade**, **Segurança**, **Governança** e **Monitoramento**.

#### **b. Arquitetura "As-Built" (2,0 pontos)**

A fidelidade entre o planejamento e a execução é fundamental em projetos de Engenharia de Dados:

-   **Correspondência Técnica:** O diagrama final deve refletir o que está operando.
-   **Documentação de Melhorias:** Caso tenha havido mudanças em relação à Parte 1, o diagrama deve ser atualizado e as alterações justificadas no README.

#### **c. Organização, Documentação e Defesa (2,0 pontos)**

A qualidade do entregável sob a ótica de engenharia de software, organização e comunicação:

-   **Padrões de Repositório:** Estrutura de pastas organizada.
-   **Documentação (README):** Instruções claras de reprodução (como rodar o projeto) e justificativa das tecnologias.
-   **Apresentação e Defesa:** Domínio do conteúdo durante a exposição, clareza na resposta às arguições e justificativa das decisões técnicas tomadas.
