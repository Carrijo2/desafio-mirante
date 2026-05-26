# Pipeline Hibrido de Modernizacao SQL para Python

**Vision:** Construir uma pipeline hibrida, baseada em LangGraph, para modernizar stored procedures PL/pgSQL em modulos Python 3.14 equivalentes, com relatorio estruturado das decisoes e validacoes de cada etapa.
**For:** Avaliadores tecnicos do desafio e times de inovacao que precisam analisar uma arquitetura reprodutivel para migracao assistida de sistemas legados.
**Solves:** Demonstra como combinar parsing deterministico, analise semantica, geracao orientada por contexto e validacao estatica para reduzir risco em traducoes de logica SQL legada.

## Goals

- Entregar uma API local com `POST /modernize` e `GET /health`, orquestrada por LangGraph, executando de ponta a ponta sobre os anexos B a F.
- Persistir toda execucao em PostgreSQL na tabela `modernization_history`, incluindo casos de sucesso, falha e resultado parcial.
- Produzir README, resultados de execucao e decisoes tecnicas suficientes para defesa em uma revisao tecnica de 45 minutos.
- Incluir ao menos uma melhoria bonus quando couber no prazo, preferencialmente QA com pytest e checks estaticos.

## Tech Stack

**Core:**

- Framework: LangGraph CLI e servidor local compativel com endpoints HTTP.
- Language: Python 3.14.
- Database: PostgreSQL.

**Key dependencies:**

- `langgraph` para orquestracao do grafo.
- Parser SQL a definir entre `pglast`, `sqlglot` ou `sqlparse`, com justificativa no README.
- Cliente PostgreSQL/ORM a definir, preferencialmente simples e explicito.
- `pytest` para testes automatizados.
- Ferramenta de lint/format a definir, preferencialmente uma opcao unica para reduzir complexidade.

## Scope

**v1 includes:**

- API local com health check e endpoint de modernizacao.
- Grafo LangGraph com nos de parsing, analise semantica, geracao e validacao.
- Estado tipado entre os nos da pipeline.
- Persistencia de historico em PostgreSQL.
- Suporte aos cinco casos obrigatorios dos anexos B a F.
- Relatorios estruturados por etapa.
- Artefatos de entrega: README, Docker Compose, scripts de banco e outputs gerados.

**Explicitly out of scope:**

- Cobertura sintatica completa de PL/pgSQL.
- Garantia formal de equivalencia comportamental para qualquer procedure arbitraria.
- Interface web.
- Multi-tenant, autenticacao, autorizacao ou deploy em producao.
- Treinamento/fine-tuning de modelo.

## Constraints

- Timeline: ate 2 dias corridos de take-home.
- Technical: Python 3.14, LangGraph, PostgreSQL e endpoints minimos exigidos pelo PDF.
- Resources: uso de bibliotecas externas e assistentes de IA e permitido, mas toda decisao deve ser defensavel e documentada.
