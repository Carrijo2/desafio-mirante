# AI-Assisted Modernization Tasks

**Design**: `.specs/features/ai-assisted-modernization/design.md`
**Status**: Done

---

## Execution Plan

### Phase 1: Provider Foundation

```text
AI-T1 -> AI-T2 -> AI-T3
```

### Phase 2: Pipeline Integration

```text
AI-T3 -> AI-T4 -> AI-T5 -> AI-T6
```

### Phase 3: Documentation and Verification

```text
AI-T6 -> AI-T7 -> AI-T8
```

---

## Task Breakdown

### AI-T1: Extend config and environment docs

**What**: Add AI environment variables and dependency placeholders.
**Where**: `.env.example`, `pyproject.toml`, README
**Depends on**: None
**Reuses**: current install/docs structure
**Requirement**: AI-01, AI-05

**Done when**:

- [ ] `.env.example` documents `AI_PROVIDER`, `AI_MODEL`, `AI_TIMEOUT_SECONDS`, `AI_REPAIR_ENABLED`.
- [ ] Provider dependency strategy is explicit.
- [ ] Running without AI env still works.

**Tests**: none
**Gate**: docs + existing test suite

**Status**: Done

---

### AI-T2: Create provider interface and factory

**What**: Implement `LlmProvider`, unavailable provider, provider factory and result models.
**Where**: `app/integrations/llm.py`
**Depends on**: AI-T1
**Reuses**: `build_generation_context`
**Requirement**: AI-01, AI-05

**Done when**:

- [ ] Provider interface has `generate` and `repair`.
- [ ] Factory returns unavailable provider when AI is disabled/misconfigured.
- [ ] Unit tests cover disabled, unsupported and enabled/mock provider paths.

**Tests**: unit
**Gate**: quick

**Status**: Done

---

### AI-T3: Add prompt builder and code extraction

**What**: Build versioned prompts from structured context and extract Python code from AI output.
**Where**: `app/integrations/llm.py`
**Depends on**: AI-T2
**Reuses**: parser and semantic report fields
**Requirement**: AI-01, AI-03

**Done when**:

- [ ] Prompt includes source, schema context, parsed summary, semantic findings and risks.
- [ ] Prompt has version/id for report traceability.
- [ ] Code extractor handles raw code and markdown fenced code.
- [ ] Tests cover extraction and prompt content.

**Tests**: unit
**Gate**: quick

**Status**: Done

---

### AI-T4: Integrate AI strategy into generation node

**What**: Update generation node to choose AI generation when available and fallback deterministically otherwise.
**Where**: `app/nodes/generation.py`
**Depends on**: AI-T3
**Reuses**: deterministic wrapper generator
**Requirement**: AI-01, AI-02, AI-03

**Done when**:

- [ ] Generation node records strategy: `ai`, `deterministic`, or `deterministic_fallback`.
- [ ] AI generation receives structured context.
- [ ] AI failure falls back to deterministic generation.
- [ ] Tests mock provider success and failure.

**Tests**: unit/integration
**Gate**: quick

**Status**: Done

---

### AI-T5: Add parser confidence and fallback triggers

**What**: Mark parser/semantic confidence and trigger AI priority when parsing is weak.
**Where**: `app/nodes/parsing.py`, `app/nodes/semantic_analysis.py`, `app/graph/state.py`
**Depends on**: AI-T4
**Reuses**: current report structure
**Requirement**: AI-02

**Done when**:

- [ ] Parser node records confidence and recoverable errors.
- [ ] Semantic node records low-confidence reasons when constructs are unknown/ambiguous.
- [ ] Generation node uses these signals to prefer AI when available.
- [ ] Tests force low-confidence path.

**Tests**: unit
**Gate**: quick

**Status**: Done

---

### AI-T6: Add one-shot AI repair path

**What**: Add optional repair attempt when AI-generated code fails `ast.parse`.
**Where**: `app/nodes/validation.py`, `app/integrations/llm.py`
**Depends on**: AI-T5
**Reuses**: provider interface and validation error
**Requirement**: AI-04

**Done when**:

- [ ] Invalid AI output triggers at most one repair when enabled.
- [ ] Repair prompt includes original code and syntax error.
- [ ] Successful repair replaces generated code and records `ai_repair`.
- [ ] Failed repair does not loop.

**Tests**: unit/integration
**Gate**: quick

**Status**: Done

---

### AI-T7: Update README and reports

**What**: Document AI behavior, env vars, fallback strategy and limitations.
**Where**: `README.md`
**Depends on**: AI-T6
**Reuses**: spec/design decisions
**Requirement**: AI-03

**Done when**:

- [ ] README explains no-key deterministic mode.
- [ ] README explains AI-enabled mode.
- [ ] README documents provider/model env vars.
- [ ] README describes what is persisted in report.

**Tests**: none
**Gate**: docs review

**Status**: Done

---

### AI-T8: Run full verification

**What**: Run tests, lint, sample generation and LangGraph validation after AI integration.
**Where**: repository root
**Depends on**: AI-T7
**Reuses**: existing QA commands
**Requirement**: AI-01, AI-02, AI-03, AI-04, AI-05

**Done when**:

- [ ] `pytest` passes.
- [ ] `ruff check .` passes.
- [ ] `python scripts/run_samples.py` succeeds without AI credentials.
- [ ] Mock-AI tests prove AI path.
- [ ] `langgraph validate --config langgraph.json` passes.

**Tests**: full suite
**Gate**: full

**Status**: Done

---

## Execution Results

- `app/integrations/llm.py` now includes provider interface, unavailable provider, OpenAI Responses provider, prompt builder, repair prompt builder and Python code extraction.
- `app/nodes/generation.py` now selects `ai`, `deterministic`, or `deterministic_fallback`.
- `app/nodes/validation.py` now supports one AI repair attempt for invalid AI-generated Python.
- `app/nodes/parsing.py` and `app/nodes/semantic_analysis.py` now report confidence signals.
- `.env.example` documents AI environment variables.
- README documents AI-enabled and deterministic modes.
- `pytest`: 13 passed.
- `ruff check .`: passed.
- `python scripts/run_samples.py`: processed annexes B, C, D, E and F with status `sucesso` without AI credentials.
- `langgraph validate --config langgraph.json`: valid, 1 graph found.
- `python -m compileall outputs app scripts`: passed.

---

## Validation Checks

### Task Granularity Check

| Task | Scope | Status |
| --- | --- | --- |
| AI-T1 | Config/docs only | OK |
| AI-T2 | Provider interface/factory | OK |
| AI-T3 | Prompt and extraction | OK |
| AI-T4 | Generation node strategy | OK |
| AI-T5 | Parser confidence/fallback trigger | OK |
| AI-T6 | Repair path | OK |
| AI-T7 | README | OK |
| AI-T8 | Final verification | OK |

### Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
| --- | --- | --- | --- |
| AI-T1 | None | Start | OK |
| AI-T2 | AI-T1 | AI-T1 -> AI-T2 | OK |
| AI-T3 | AI-T2 | AI-T2 -> AI-T3 | OK |
| AI-T4 | AI-T3 | AI-T3 -> AI-T4 | OK |
| AI-T5 | AI-T4 | AI-T4 -> AI-T5 | OK |
| AI-T6 | AI-T5 | AI-T5 -> AI-T6 | OK |
| AI-T7 | AI-T6 | AI-T6 -> AI-T7 | OK |
| AI-T8 | AI-T7 | AI-T7 -> AI-T8 | OK |

### Test Co-location Validation

| Task | Code Layer Created/Modified | Task Says | Status |
| --- | --- | --- | --- |
| AI-T1 | Config/docs | none | OK |
| AI-T2 | Integration/provider | unit | OK |
| AI-T3 | Prompt/extraction utilities | unit | OK |
| AI-T4 | Generation node | unit/integration | OK |
| AI-T5 | Parsing/semantic/state | unit | OK |
| AI-T6 | Validation/provider | unit/integration | OK |
| AI-T7 | Docs | none | OK |
| AI-T8 | Whole project | full suite | OK |
