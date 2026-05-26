# Pipeline de Modernizacao SQL para Python Specification

## Problem Statement

O desafio exige uma pipeline hibrida capaz de receber stored procedures PL/pgSQL e produzir codigo Python 3.14 equivalente, acompanhado de relatorio de parsing, analise, geracao e validacao. A solucao precisa ser executavel localmente, persistir cada execucao em PostgreSQL e ser clara o suficiente para defesa tecnica posterior.

## Goals

- [ ] Disponibilizar servidor local com `GET /health` e `POST /modernize`.
- [ ] Orquestrar parsing, analise semantica, geracao e validacao como nos de um grafo LangGraph com estado tipado.
- [ ] Persistir toda execucao em `modernization_history`, independentemente do desfecho.
- [ ] Processar os anexos B a F e versionar os resultados gerados.
- [ ] Documentar arquitetura, decisoes, trade-offs, execucao local, testes e limitacoes.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Parser PL/pgSQL completo | O PDF avalia desenho da pipeline e decisoes de traducao, nao cobertura total da linguagem. |
| UI web | Nao e solicitada; a entrega e API + repositorio. |
| Deploy em cloud | Escopo take-home local. |
| Autenticacao/autorizacao | Nao consta nos requisitos do desafio. |
| Garantia formal de equivalencia | Pode ser evolucao futura; MVP usa validacoes estaticas e casos anexos. |

---

## User Stories

### P1: Executar modernizacao via API

**User Story**: As an avaliador tecnico, I want enviar uma stored procedure para um endpoint local so that eu consiga observar a pipeline completa gerando Python 3.14 e relatorio estruturado.

**Why P1**: E o fluxo principal e responde diretamente ao requisito `POST /modernize`.

**Acceptance Criteria**:

1. WHEN `GET /health` is called THEN system SHALL return HTTP 200 with `{"status": "ok"}` or equivalent.
2. WHEN `POST /modernize` receives valid PL/pgSQL THEN system SHALL return generated Python 3.14, structured report and final status.
3. WHEN optional schema context is provided THEN system SHALL make it available to generation and report stages.
4. WHEN the input is invalid or an internal stage fails THEN system SHALL return a controlled error/status without losing the execution record.

**Independent Test**: Call both endpoints locally and verify response shape, status and persistence.

---

### P1: Orquestrar pipeline com LangGraph

**User Story**: As an avaliador tecnico, I want cada etapa modelada como no de grafo so that a arquitetura da pipeline fique explicita, modular e extensivel.

**Why P1**: LangGraph com nos e estado tipado e requisito obrigatorio.

**Acceptance Criteria**:

1. WHEN a modernization run starts THEN system SHALL execute parsing, semantic analysis, generation and validation as graph nodes.
2. WHEN each node completes THEN system SHALL append its findings to the structured report.
3. WHEN a node fails THEN system SHALL mark the run as `falha` or `parcial` and include diagnostic details in the report.
4. WHEN the README is read THEN it SHALL include a textual or visual diagram of the graph.

**Independent Test**: Run one procedure and inspect logs/report to confirm all nodes executed in order.

---

### P1: Produzir representacao estruturada e analise semantica

**User Story**: As an implementador da migracao, I want transformar SQL em estrutura intermediaria e identificar riscos so that a geracao nao dependa apenas do SQL bruto.

**Why P1**: O PDF exige parsing e analise semantica antes da geracao.

**Acceptance Criteria**:

1. WHEN SQL is parsed THEN system SHALL produce AST, token tree or equivalent intermediate representation.
2. WHEN semantic analysis runs THEN system SHALL identify parameters IN/OUT, variables, cursors, transactions, exceptions, CTEs, nested calls and relevant SQL constructs when present.
3. WHEN risky constructs are found THEN system SHALL tag risks such as cursor/N+1, `RAISE`, `FOR UPDATE`, JSONB, recursion and nested database functions.
4. WHEN parser limitations are hit THEN system SHALL preserve enough context for generation and clearly report the limitation.

**Independent Test**: Process annexes B to F and verify the report captures the expected constructs listed in the PDF complexity map.

---

### P1: Gerar codigo Python 3.14 equivalente

**User Story**: As an avaliador tecnico, I want receber modulo Python plausivelmente equivalente so that eu consiga avaliar as escolhas de traducao da pipeline.

**Why P1**: Geracao de Python 3.14 e o produto central do desafio.

**Acceptance Criteria**:

1. WHEN generation runs THEN system SHALL use parser and semantic outputs as explicit context.
2. WHEN SQL should remain delegated to PostgreSQL THEN system SHALL keep SQL text or SQL builder usage intentionally and document why.
3. WHEN logic is translated to Python THEN system SHALL produce readable Python 3.14 with typed function signatures where practical.
4. WHEN output parameters or set-returning functions are present THEN system SHALL choose and document a Python representation such as dict, dataclass, tuple or iterable rows.
5. WHEN generated code contains assumptions THEN system SHALL include them in the report.

**Independent Test**: Generate Python for each annex and inspect code plus decisions in the report.

---

### P1: Validar e persistir cada execucao

**User Story**: As an avaliador tecnico, I want toda execucao persistida com validacao so that resultados sejam auditaveis mesmo em falhas.

**Why P1**: Persistencia e validacao estatica sao requisitos obrigatorios.

**Acceptance Criteria**:

1. WHEN generated Python is produced THEN system SHALL run `ast.parse` against it.
2. WHEN lint/static checks are configured THEN system SHALL include their result in the validation report.
3. WHEN execution finishes with success, partial success or failure THEN system SHALL insert one row in `modernization_history`.
4. WHEN a row is inserted THEN it SHALL include `id`, `source_code`, `generated_code`, `report`, `status` and `created_at`.

**Independent Test**: Run successful and invalid inputs, then query `modernization_history` for both records.

---

### P2: Entregar resultados dos anexos B a F

**User Story**: As an avaliador tecnico, I want ver os outputs dos cinco anexos obrigatorios so that eu consiga comparar complexidades e avaliar o comportamento da pipeline.

**Why P2**: E exigido como artefato de entrega, mas depende da pipeline funcionando.

**Acceptance Criteria**:

1. WHEN the sample runner is executed THEN system SHALL process annexes B, C, D, E and F.
2. WHEN each annex is processed THEN system SHALL store generated Python and report in a deterministic output folder.
3. WHEN README references samples THEN paths and commands SHALL match the repository.

**Independent Test**: Run the sample command and verify five result sets are created.

---

### P2: QA automatizado

**User Story**: As an implementador, I want testes e checks estaticos so that a entrega tenha confiabilidade e ganhe aderencia ao bonus de QA.

**Why P2**: Melhora pontuacao em codigo/estrutura e cobre um bonus viavel no prazo.

**Acceptance Criteria**:

1. WHEN tests run THEN pytest SHALL cover API health, modernization happy path, persistence and at least one failure path.
2. WHEN quality checks run THEN lint/format/type checks configured SHALL pass.
3. WHEN README documents QA THEN it SHALL include the exact commands.

**Independent Test**: Run documented QA commands from a clean checkout.

---

### P3: Metrica de evaluation

**User Story**: As an avaliador tecnico, I want uma metrica automatica de qualidade so that eu consiga comparar execucoes da pipeline.

**Why P3**: Bonus interessante, mas nao deve bloquear MVP.

**Acceptance Criteria**:

1. WHEN annexes B to F are processed THEN system SHALL compute at least one metric such as parse success rate, completed run rate or AST validation pass rate.
2. WHEN metric is computed THEN system SHALL record the result in a table, artifact, endpoint or observability tool.
3. WHEN README explains the metric THEN it SHALL describe what it captures, what it misses and how it would evolve.

**Independent Test**: Run evaluation command and verify metric output.

---

### P3: Observabilidade com Langfuse ou LangSmith

**User Story**: As an avaliador tecnico, I want traces por execucao so that eu consiga visualizar spans dos nos e custo/latencia de LLM quando aplicavel.

**Why P3**: Bonus valioso, mas depende de setup adicional e pode ser adiado se comprometer MVP.

**Acceptance Criteria**:

1. WHEN observability is enabled THEN each graph run SHALL create a trace.
2. WHEN nodes execute THEN spans SHALL identify parsing, semantic analysis, generation and validation.
3. WHEN README documents observability THEN it SHALL include setup and evidence visual ou caminho para reproduzir.

**Independent Test**: Enable observability locally and inspect trace for one annex.

## Edge Cases

- WHEN input SQL is empty THEN system SHALL reject the request with validation error and persist a failed run when execution record has started.
- WHEN parser cannot fully parse PL/pgSQL THEN system SHALL mark parser limitations and continue only if enough structured context exists.
- WHEN LLM credentials are absent and generation depends on LLM THEN system SHALL fail clearly or use a deterministic fallback if implemented.
- WHEN database is unavailable THEN system SHALL return a controlled error and avoid reporting success.
- WHEN generated Python is syntactically invalid THEN system SHALL mark validation failure and persist status `parcial` or `falha`.
- WHEN a procedure uses cursor loops THEN system SHALL flag potential N+1/performance risk.
- WHEN a procedure uses transactions or `FOR UPDATE` THEN system SHALL flag transactional semantics and locking risk.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| MOD-01 | P1: Executar modernizacao via API | Design | Pending |
| MOD-02 | P1: Orquestrar pipeline com LangGraph | Design | Pending |
| MOD-03 | P1: Produzir representacao estruturada e analise semantica | Design | Pending |
| MOD-04 | P1: Gerar codigo Python 3.14 equivalente | Design | Pending |
| MOD-05 | P1: Validar e persistir cada execucao | Design | Pending |
| MOD-06 | P2: Entregar resultados dos anexos B a F | Design | Pending |
| MOD-07 | P2: QA automatizado | Design | Pending |
| MOD-08 | P3: Metrica de evaluation | Design | Pending |
| MOD-09 | P3: Observabilidade com Langfuse ou LangSmith | Design | Pending |

**Coverage:** 9 total, 9 mapped to design, 0 verified.

---

## Success Criteria

- [ ] `docker compose up` or documented equivalent starts API and PostgreSQL locally.
- [ ] `GET /health` returns success.
- [ ] `POST /modernize` returns generated Python, report and status.
- [ ] Five annex procedures are processed and outputs are committed.
- [ ] `modernization_history` contains one row per execution.
- [ ] README explains graph, decisions, trade-offs, limitations and local commands.
- [ ] Tests/checks documented in README pass locally.
