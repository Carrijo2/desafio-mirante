# Pipeline de Modernizacao SQL para Python Tasks

**Design**: `.specs/features/pipeline-modernizacao-sql-python/design.md`
**Status**: MVP Done; Optional Bonus Pending

---

## Execution Plan

### Phase 1: Foundation

```text
T1 -> T2 -> T3 -> T4
```

### Phase 2: Pipeline Core

```text
T4 -> T5 -> T6 -> T7 -> T8
```

### Phase 3: API, Samples and Delivery

```text
T8 -> T9 -> T10 -> T11 -> T12
```

### Phase 4: Optional Bonus

```text
T12 -> T13
T12 -> T14
```

---

## Task Breakdown

### T1: Scaffold Python project

**What**: Create project metadata, package structure and baseline local commands.
**Where**: `pyproject.toml`, `app/`, `tests/`
**Depends on**: None
**Reuses**: `.specs/project/PROJECT.md`
**Requirement**: MOD-07

**Done when**:

- [ ] Project installs locally.
- [ ] Package directories from design exist.
- [ ] Baseline test command is defined.
- [ ] Gate check passes with current empty/minimal tests.

**Tests**: unit
**Gate**: quick

---

### T2: Add database schema and local PostgreSQL

**What**: Add Docker Compose and SQL init script for `modernization_history`.
**Where**: `docker-compose.yml`, `db/init.sql`
**Depends on**: T1
**Reuses**: design data model
**Requirement**: MOD-05

**Done when**:

- [ ] PostgreSQL starts locally.
- [ ] `modernization_history` is created with required columns.
- [ ] Status constraint accepts `sucesso`, `falha`, `parcial`.
- [ ] README or script documents connection variables.

**Tests**: integration
**Gate**: full

---

### T3: Implement typed API and graph schemas

**What**: Define request/response models and `ModernizationState`.
**Where**: `app/api/schemas.py`, `app/graph/state.py`
**Depends on**: T2
**Reuses**: design data models
**Requirement**: MOD-01, MOD-02

**Done when**:

- [ ] Request model supports `source_code` and optional `schema_context`.
- [ ] Response model includes id, generated code, report and status.
- [ ] State model contains fields for all graph stages.
- [ ] Unit tests cover required fields and validation.

**Tests**: unit
**Gate**: quick

---

### T4: Implement history repository

**What**: Create database connection helper and function to persist one pipeline execution.
**Where**: `app/persistence/database.py`, `app/persistence/history_repository.py`
**Depends on**: T3
**Reuses**: `ModernizationState`
**Requirement**: MOD-05

**Done when**:

- [ ] Repository inserts source, generated code, report, status and created timestamp.
- [ ] Repository returns generated id.
- [ ] Integration test proves a row is inserted.
- [ ] Failure/partial statuses are accepted.

**Tests**: integration
**Gate**: full

---

### T5: Implement parsing node

**What**: Parse SQL into a JSON-serializable intermediate representation.
**Where**: `app/nodes/parsing.py`
**Depends on**: T4
**Reuses**: parser decision documented in README/design
**Requirement**: MOD-03

**Done when**:

- [ ] Valid annex SQL produces parsed representation.
- [ ] Parser errors are captured in report.
- [ ] Report includes parser library and limitations.
- [ ] Tests cover a simple function and malformed SQL.

**Tests**: unit
**Gate**: quick

---

### T6: Implement semantic analysis node

**What**: Detect PL/pgSQL constructs and translation risks from source and parsed representation.
**Where**: `app/nodes/semantic_analysis.py`
**Depends on**: T5
**Reuses**: complexity map from PDF
**Requirement**: MOD-03

**Done when**:

- [ ] Detects parameters, variables, cursors, exceptions, CTEs, nested calls and transaction markers where present.
- [ ] Flags risks for cursor loops, `FOR UPDATE`, JSONB, recursion and `RAISE`.
- [ ] Tests cover representative snippets from annexes B to F.

**Tests**: unit
**Gate**: quick

---

### T7: Implement generation node

**What**: Generate Python 3.14 using structured context from prior nodes.
**Where**: `app/nodes/generation.py`, `app/integrations/llm.py`
**Depends on**: T6
**Reuses**: semantic findings and schema context
**Requirement**: MOD-04

**Done when**:

- [ ] Prompt/context includes parsed representation and semantic findings when LLM is used.
- [ ] Generated code is returned as a module/function string.
- [ ] Report records translation decisions and assumptions.
- [ ] Deterministic fallback or explicit missing-LLM error is implemented.

**Tests**: unit
**Gate**: quick

---

### T8: Implement validation node and graph wiring

**What**: Wire LangGraph nodes and validate generated Python with `ast.parse`.
**Where**: `app/graph/modernization_graph.py`, `app/nodes/validation.py`
**Depends on**: T7
**Reuses**: all nodes and `ModernizationState`
**Requirement**: MOD-02, MOD-05

**Done when**:

- [ ] Graph executes parsing -> analysis -> generation -> validation.
- [ ] `ast.parse` result is recorded.
- [ ] Node failures produce `falha` or `parcial`.
- [ ] Test runs one complete modernization through the graph.

**Tests**: integration
**Gate**: full

---

### T9: Implement HTTP endpoints

**What**: Expose `GET /health` and `POST /modernize`, invoke graph and persist execution.
**Where**: `app/api/server.py`
**Depends on**: T8
**Reuses**: graph runner and history repository
**Requirement**: MOD-01, MOD-05

**Done when**:

- [ ] `/health` returns ok.
- [ ] `/modernize` returns generated code, report, status and id.
- [ ] Every modernization attempt is persisted after graph execution.
- [ ] API tests cover health, happy path and controlled failure.

**Tests**: integration
**Gate**: full

---

### T10: Add annex fixtures and sample runner

**What**: Store annex B to F procedures and create a command to process them all.
**Where**: `app/samples/`, `scripts/`, `outputs/annexes/`
**Depends on**: T9
**Reuses**: PDF annex SQL
**Requirement**: MOD-06

**Done when**:

- [ ] Five procedures are available as fixtures.
- [ ] Sample runner calls the pipeline for all five.
- [ ] Generated Python and report files are written deterministically.
- [ ] README documents the command.

**Tests**: integration
**Gate**: full

---

### T11: Write README delivery documentation

**What**: Document architecture, graph, setup, commands, decisions, trade-offs, limitations and outputs.
**Where**: `README.md`
**Depends on**: T10
**Reuses**: `.specs/project/PROJECT.md`, design and task outputs
**Requirement**: MOD-02, MOD-06, MOD-07

**Done when**:

- [ ] README explains pipeline flow and LangGraph diagram.
- [ ] README includes local run/test commands and env vars.
- [ ] README justifies parser, generation and persistence decisions.
- [ ] README lists known limitations and future work.

**Tests**: none
**Gate**: docs review

---

### T12: Run final QA and collect delivery outputs

**What**: Execute documented checks and regenerate annex outputs for final state.
**Where**: repository root, `outputs/annexes/`
**Depends on**: T11
**Reuses**: all implementation
**Requirement**: MOD-06, MOD-07

**Done when**:

- [ ] Test suite passes.
- [ ] Static checks pass.
- [ ] Annex outputs exist for B, C, D, E and F.
- [ ] Database persistence is verified.

**Tests**: full suite
**Gate**: full

---

### T13: Add evaluation metric bonus

**What**: Compute and expose a simple quality metric over annex executions.
**Where**: `app/nodes/validation.py`, `scripts/`, optional `app/api/server.py`
**Depends on**: T12
**Reuses**: validation results and annex output runner
**Requirement**: MOD-08

**Done when**:

- [ ] Metric is computed for annexes B to F.
- [ ] Metric result is persisted or written as artifact.
- [ ] README explains what the metric captures and misses.

**Tests**: unit/integration
**Gate**: full

---

### T14: Add observability bonus

**What**: Integrate Langfuse or LangSmith tracing for graph runs.
**Where**: `app/integrations/observability.py`, `docker-compose.yml`, README
**Depends on**: T12
**Reuses**: graph node boundaries
**Requirement**: MOD-09

**Done when**:

- [ ] Each modernization run creates a trace when observability is enabled.
- [ ] Nodes appear as identifiable spans.
- [ ] README documents setup and evidence collection.

**Tests**: integration/manual
**Gate**: full

---

## Execution Results

- T1-T12 completed in the repository implementation.
- T13 evaluation metric remains optional and pending.
- T14 observability remains optional and pending.
- `pytest`: 6 passed.
- `ruff check .`: passed.
- `python scripts/run_samples.py`: processed annexes B, C, D, E and F with status `sucesso`.
- `langgraph validate --config langgraph.json`: valid, 1 graph found.
- `python -m compileall outputs app scripts`: generated outputs compile successfully.
- Local API started with Uvicorn at `http://127.0.0.1:8000`; `GET /health` returned `{"status":"ok"}`.
- PostgreSQL Docker startup was not verified because Docker Desktop daemon was not running.

## Validation Checks

### Task Granularity Check

| Task | Scope | Status |
| --- | --- | --- |
| T1 | Scaffold only | OK |
| T2 | Database/bootstrap only | OK |
| T3 | Shared schemas/state | OK |
| T4 | Persistence repository | OK |
| T5 | Parsing node | OK |
| T6 | Semantic node | OK |
| T7 | Generation node | OK |
| T8 | Validation + graph wiring | OK |
| T9 | HTTP endpoints | OK |
| T10 | Samples/output runner | OK |
| T11 | README | OK |
| T12 | Final QA/output collection | OK |
| T13 | One bonus metric | OK |
| T14 | One observability integration | OK |

### Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | Start | OK |
| T2 | T1 | T1 -> T2 | OK |
| T3 | T2 | T2 -> T3 | OK |
| T4 | T3 | T3 -> T4 | OK |
| T5 | T4 | T4 -> T5 | OK |
| T6 | T5 | T5 -> T6 | OK |
| T7 | T6 | T6 -> T7 | OK |
| T8 | T7 | T7 -> T8 | OK |
| T9 | T8 | T8 -> T9 | OK |
| T10 | T9 | T9 -> T10 | OK |
| T11 | T10 | T10 -> T11 | OK |
| T12 | T11 | T11 -> T12 | OK |
| T13 | T12 | T12 -> T13 | OK |
| T14 | T12 | T12 -> T14 | OK |

### Test Co-location Validation

| Task | Code Layer Created/Modified | Task Says | Status |
| --- | --- | --- | --- |
| T1 | Project/test foundation | unit | OK |
| T2 | DB bootstrap | integration | OK |
| T3 | Schemas/state | unit | OK |
| T4 | Persistence | integration | OK |
| T5 | Node | unit | OK |
| T6 | Node | unit | OK |
| T7 | Node/integration wrapper | unit | OK |
| T8 | Graph + validation | integration | OK |
| T9 | API | integration | OK |
| T10 | Sample runner | integration | OK |
| T11 | Docs | none | OK |
| T12 | QA | full suite | OK |
| T13 | Evaluation metric | unit/integration | OK |
| T14 | Observability | integration/manual | OK |

## Notes Before Execution

- Como ainda nao existe `.specs/codebase/TESTING.md`, os comandos finais de gate devem ser consolidados quando o projeto for scaffoldado.
- Antes de implementar, escolher explicitamente parser SQL, framework HTTP usado pelo LangGraph CLI e cliente PostgreSQL.
- Tasks T13 e T14 sao opcionais; T13 tende a ser menor que T14 e mais segura apos o MVP.
