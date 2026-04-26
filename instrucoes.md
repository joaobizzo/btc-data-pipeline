# **Projeto: Protótipo de Ciclo de Vida de Engenharia de Dados (Parte 1)**

# **1\. Apresentação**

Esta atividade constitui a 1ª avaliação da disciplina. O grupo deverá iniciar o desenvolvimento de um projeto que, ao longo do semestre, se tornará um protótipo de um ciclo de vida completo de engenharia de dados. Nesta primeira parte, o foco é o planejamento e o desenho arquitetural do projeto, aplicando os conceitos vistos nas Aulas 01 a 05 (arquitetura de dados, princípios de engenharia de dados, domínios e serviços, escalabilidade, acoplamento, tipos de arquitetura como Data Warehouse, Data Lake, Lakehouse, Lambda/Kappa, Data Mesh, etc.).

# **2\. Formato do Trabalho**

•        Pode ser realizado individualmente, em dupla ou em trio.

•        Entregas: (a) Repositório no GitHub (encaminhar aqui na atividade um pdf com o link e um print do repositório público) e (b) apresentação em sala.

•        Data da apresentação: 30/04/2026.

•        Data limite de entrega do relatório: ver na atividade

•        Tema livre: o grupo escolhe um cenário/negócio (ex.: e-commerce, IoT agrícola, streaming de música, rede hospitalar, plataforma de mobilidade urbana, etc.).

# **3\. Objetivo**

Planejar a primeira parte de um protótipo de ciclo de vida de engenharia de dados, definindo claramente o que será feito (fluxo de dados, domínios, serviços) e como será feito (tecnologias escolhidas e justificadas). A segunda parte do projeto, em avaliação futura, consistirá na implementação prática do que foi planejado aqui. Planeje algo viável. Lembre-se das limitações da sua máquina ou das máquinas da sala.

# **4\. O que deve ser entregue no Repositório do GitHub**

O repositório deve conter os seguintes conteúdos (Dica: use arquivos .md e o mermaid):

## **4.1. Descrição do Projeto**

•        Nome do projeto e contexto de negócio escolhido.

•        Problema que o projeto pretende resolver e objetivos principais.

•        Principais stakeholders/usuários finais dos dados.

## **4.2. Definição e Classificação dos Dados**

•        Quais dados serão utilizados no projeto (fontes, formatos, volume estimado, frequência).

•        Classificação explícita em:

◦        Dados operacionais (batch, transacionais, históricos, estruturados em bancos relacionais etc.).

◦        Dados de streaming (eventos em tempo real, sensores, logs, cliques, filas de mensagens etc.).

•        Detalhes de cada fonte: origem, formato (JSON, CSV, Parquet, Avro...), periodicidade e latência esperada.

## **4.3. Domínios e Serviços**

•        Identificação dos domínios de negócio envolvidos (ex.: Vendas, Estoque, Financeiro, Logística, Marketing).

•        Serviços que compõem cada domínio e eventuais serviços compartilhados entre domínios.

•        Diagrama simples dos domínios e serviços, indicando responsabilidades.

## **4.4. Arquitetura — O que será feito (Fluxo de Dados)**

•        Diagrama da arquitetura mostrando o fluxo ponta a ponta: origem dos dados → ingestão → armazenamento → transformação → serviço de dados (consumo).

•        Indicar claramente os caminhos de batch e de streaming (quando aplicável).

•        Justificar o tipo de arquitetura escolhida (ex.: Data Warehouse, Data Lake, Lakehouse, Lambda, Kappa, Data Mesh, Arquitetura Medalhão etc.) com base nos conceitos vistos em aula.

•        Discutir brevemente trade-offs: acoplamento, escalabilidade, disponibilidade, confiabilidade e reversibilidade das decisões.

## **4.5. Tecnologias — Como será feito**

Para cada etapa do ciclo de vida, detalhar as tecnologias escolhidas e justificar a escolha. Não basta listar. É preciso explicar o porquê de cada uma e como elas se integram.

•        Ingestão (ex.: Apache Kafka, AWS Kinesis, Airbyte, Fivetran, NiFi).

•        Armazenamento (ex.: PostgreSQL, S3/GCS/Azure Blob, BigQuery, Snowflake, Redshift, Delta Lake).

•        Processamento e transformação (ex.: Apache Spark, dbt, Flink, Beam, pandas).

•        Orquestração (ex.: Airflow, Prefect, Dagster).

•        Servir dados/consumo (ex.: Power BI, Metabase, Superset, APIs, ML, ETL reverso).

•        Correntes do ciclo de vida: segurança, gestão de dados, DataOps, monitoramento, governança.

Observação: é permitido (e incentivado) considerar ferramentas open-source e/ou serviços gerenciados em nuvem (AWS, GCP, Azure). O importante é que o grupo saiba justificar as escolhas.

## **4.6. Considerações Finais**

•        Principais riscos e limitações previstos.

•        Próximos passos para a Parte 2 do projeto (implementação).

•        Referências utilizadas.

# **5\. Apresentação em Sala**

•        Duração: 10 a 20 minutos por grupo, seguidos de perguntas.

•        Todos os integrantes devem apresentar alguma parte.

# **6\. Critérios de Avaliação**

A nota final é composta pelo repositório no GitHub e pela apresentação, conforme a tabela abaixo:

| Critério | Descrição | Peso |
| :--- | :--- | :--- |
| **Definição do escopo e dados** | Clareza na definição do projeto, identificação e classificação dos dados (operacionais vs. streaming). | 2,0 |
| **Domínios e serviços** | Identificação coerente dos domínios de negócio e dos serviços envolvidos. | 2,0 |
| **Arquitetura e fluxo de dados** | Diagrama e descrição do fluxo (o que será feito), alinhado aos princípios vistos em aula. | 2,0 |
| **Tecnologias (como será feito)** | Detalhamento e justificativa das tecnologias escolhidas em cada etapa do ciclo de vida. | 2,0 |
| **Relato e apresentação** | Qualidade da escrita, organização, clareza da apresentação e domínio do conteúdo. | 2,0 |
| **Total** | | **10,0** |

# **7\. Entrega**

•        Relatório em PDF enviado até 30/04/2026.

•        Apresentação em sala no dia 30/04/2026.

•        Identificar no relatório: nome completo dos integrantes, matrícula e nome do projeto.

# **8\. Observações Importantes**

•        Não é necessário implementar nada nesta parte. O foco é o planejamento arquitetural. Mas é importante fazer pequenas provas de conceito para validarem e justificar a escolha das tecnologias.

•        Sejam pragmáticos: escolham um escopo realista, que possa ser implementado na Parte 2.

•        Dúvidas podem ser encaminhadas pelo e-mail luis.ccardoso@ceub.edu.br.
