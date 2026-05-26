# Roadmap

**Current Milestone:** MVP avaliavel do desafio tecnico
**Status:** Planning

---

## Milestone 1: Fundacao executavel

**Goal:** Ter projeto local reproduzivel com API, banco e estrutura modular.
**Target:** Aplicacao sobe localmente via instrucoes documentadas.

### Features

**API e bootstrap local** - PLANNED

- `GET /health` retorna status do pipeline.
- `POST /modernize` aceita source SQL e schema opcional.
- Docker Compose sobe servidor local e PostgreSQL.

**Persistencia de historico** - PLANNED

- Script cria `modernization_history`.
- Toda execucao e persistida com source, generated code, report, status e timestamp.

---

## Milestone 2: Pipeline hibrida obrigatoria

**Goal:** Executar o fluxo LangGraph completo com quatro etapas e estado tipado.
**Target:** Anexos B a F passam pela pipeline e geram codigo Python + relatorio.

### Features

**Grafo LangGraph** - PLANNED

- Nos separados para parsing, analise semantica, geracao e validacao.
- Estado tipado compartilhado entre os nos.
- Relatorio acumulado durante a execucao.

**Parsing e analise semantica** - PLANNED

- Parser SQL produz estrutura intermediaria.
- Analise detecta parametros, variaveis, cursores, transacoes, excecoes, CTEs, chamadas internas e riscos.

**Geracao Python 3.14** - PLANNED

- Codigo gerado a partir da estrutura intermediaria e da analise, nao apenas do SQL bruto.
- Decisoes de traducao sao registradas no relatorio.

**Validacao** - PLANNED

- `ast.parse` valida sintaxe do Python gerado.
- Lint/check estatico roda quando configurado.
- Falhas retornam status parcial ou falha e sao persistidas.

---

## Milestone 3: Entrega e diferenciadores

**Goal:** Preparar o repositorio para avaliacao tecnica e defesa.
**Target:** README completo, outputs dos anexos e pelo menos um bonus escolhido.

### Features

**Documentacao de avaliacao** - PLANNED

- README explica pipeline, grafo LangGraph, execucao local, testes, decisoes, trade-offs e limitacoes.
- Resultados dos anexos B a F sao versionados.

**QA bonus** - PLANNED

- Testes com pytest cobrem API, nos principais e persistencia.
- Checks estaticos passam localmente.

**Evaluation metric bonus** - PLANNED

- Metrica automatica calcula qualidade basica da migracao sobre anexos B a F.
- Resultado fica exposto via artefato, endpoint simples ou tabela.

**AI-assisted modernization** - PLANNED

- Provider LLM configuravel por variaveis de ambiente.
- AI usada na geracao quando configurada.
- Fallback AI para parser/analise de baixa confianca.
- Fallback deterministico preservado quando AI nao estiver disponivel.

**Observabilidade bonus** - PLANNED

- Langfuse ou LangSmith pode ser integrado se houver tempo apos MVP e QA.

## Future Considerations

- Suporte a outros dialetos SQL, como T-SQL e PL/SQL.
- Fila assincrona para processar execucoes longas.
- Cache de parsing/analise para procedures repetidas.
- Validacao comportamental contra banco legado de teste.
- Politica de modelos LLM por custo, latencia e criticidade.
