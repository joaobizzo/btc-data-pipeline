## 📌 Nome do Projeto

**Btc Data Pipeline – Monitoramento Inteligente de Preços de Bitcoin**

* * *

## 📖 Contexto

O mercado de criptomoedas é altamente volátil, exigindo monitoramento constante por parte de investidores. No entanto, muitas soluções disponíveis não oferecem um equilíbrio adequado entre granularidade recente e eficiência no armazenamento histórico.

* * *

## ❗ Problema

Investidores precisam visualizar:

-   histórico de longo prazo (anos)
-   comportamento recente com alta resolução (dias/semanas)

Mas armazenar todos os dados com alta frequência gera alto custo e complexidade.

* * *

## 🎯 Objetivo

Desenvolver um pipeline de dados que:

-   colete preços de Bitcoin em USD
-   colete taxa de câmbio USD/BRL
-   armazene histórico com granularidade variável:
    -   diário (longo prazo)
    -   4h (último mês)
    -   2h (última semana)
-   recupere dados faltantes automaticamente (backfill)
-   disponibilize dados para análise e visualização
* * *

## 👥 Stakeholders

-   Investidores individuais
-   Usuários da aplicação de portfólio
-   Desenvolvedores de sistemas financeiros
