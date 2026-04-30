## Considerações Finais

O projeto proposto estabelece uma base sólida para a construção de um pipeline de dados voltado ao monitoramento de criptomoedas, contemplando ingestão contínua, processamento histórico e organização em camadas (Bronze e Silver). A arquitetura definida busca equilibrar simplicidade de implementação com conceitos relevantes de engenharia de dados, como separação de responsabilidades, reprocessamento e resiliência.

---

## Riscos e Limitações

- Dependência de APIs externas, como a CoinGecko, sujeitas a indisponibilidade, mudanças de contrato ou rate limiting  
- Falhas de conexão durante a ingestão, podendo gerar lacunas nos dados coletados  
- Possíveis inconsistências entre dados coletados em tempo real e dados históricos  
- Aumento do volume de dados ao longo do tempo, impactando armazenamento e performance  
- Limitações de granularidade dos dados históricos dependendo do endpoint utilizado  

---

## Desafios em Aberto

- Definição de uma estratégia robusta para gerenciamento de granularidade ao longo do tempo, especialmente para:
- redução de dados antigos (downsampling)
- manutenção de maior resolução em períodos recentes  
- Garantia de consistência entre diferentes granularidades (2h, 4h e diário)  
- Definição de como lidar com possíveis divergências entre dados coletados e dados reconstruídos via backfill  

---

## Integração com o Sistema Existente

Um dos pontos futuros mais relevantes será a integração do pipeline de dados com o sistema já existente de backend e frontend.

Os principais desafios incluem:

- Definir contratos claros de dados entre o pipeline e a API do backend  
- Garantir que os dados estejam disponíveis em formatos adequados para consumo pela aplicação  
- Evitar acoplamento excessivo entre a camada de dados e a aplicação  

---

## Próximos Passos

- Implementar o pipeline de ingestão de dados (tempo real e batch)  
- Desenvolver a lógica de detecção de lacunas e backfill  
- Implementar as transformações da camada Silver  
- Estruturar o armazenamento de dados (tabelas e índices)  
- Construir dashboards iniciais para validação dos dados  
- Iniciar a integração com o backend existente  
