# AI-Assisted Modernization Specification

## Problem Statement

O MVP atual gera wrappers Python deterministas e nao chama nenhum modelo de AI. Para procedures diferentes dos anexos conhecidos, ou quando o parsing com `sqlparse` for insuficiente, a pipeline precisa usar uma camada LLM configuravel que receba contexto estruturado e produza codigo Python 3.14 mais adaptado, mantendo fallback seguro e relatorio auditavel.

## Goals

- [ ] Adicionar provider LLM configuravel por variaveis de ambiente, sem acoplar a pipeline a um unico modelo.
- [ ] Usar AI na etapa de geracao quando habilitada.
- [ ] Acionar AI como fallback quando parsing/analise deterministica detectar baixa confianca ou erro recuperavel.
- [ ] Validar a saida da AI com `ast.parse` e, se falhar, tentar reparo controlado ou retornar `parcial`/`falha`.
- [ ] Registrar prompt, provider, modelo, modo de uso, decisoes, tokens/custo quando disponivel e erros no report.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Garantia de equivalencia perfeita | LLM melhora cobertura, mas nao prova equivalencia comportamental. |
| Fine-tuning | Nao e necessario para o desafio. |
| Dependencia obrigatoria de chave AI | A pipeline deve continuar rodando sem AI via fallback deterministico. |
| Envio de segredos no report | Prompts podem ser registrados, chaves nunca. |

---

## User Stories

### P1: Geracao com AI quando configurada

**User Story**: As an avaliador tecnico, I want a pipeline use AI when configured so that procedures beyond the known annexes can receive richer Python translations.

**Why P1**: O enunciado espera uma pipeline hibrida `LLM + Rules`, nao apenas rules.

**Acceptance Criteria**:

1. WHEN `AI_PROVIDER` and required credentials are configured THEN system SHALL call the LLM generation provider.
2. WHEN AI generation runs THEN system SHALL build the prompt from `source_code`, `schema_context`, parsed representation and semantic findings.
3. WHEN the LLM returns code THEN system SHALL extract only Python code for validation.
4. WHEN the LLM is unavailable THEN system SHALL use deterministic generation fallback and report the reason.

**Independent Test**: Mock the provider and verify generation uses structured context rather than only raw SQL.

---

### P1: AI fallback for parser/heuristic limitations

**User Story**: As an implementador da migracao, I want parser failures or low-confidence analysis to trigger AI assistance so that unsupported procedures still receive a best-effort modernization.

**Why P1**: Procedures reais podem divergir dos anexos e expor limites do `sqlparse`.

**Acceptance Criteria**:

1. WHEN parsing fails with recoverable error THEN system SHALL mark parser status and continue to AI-assisted generation if AI is enabled.
2. WHEN semantic analysis detects low confidence THEN system SHALL include that reason in the LLM prompt.
3. WHEN AI fallback succeeds THEN system SHALL return status `sucesso` or `parcial` depending on validation result.
4. WHEN AI fallback fails THEN system SHALL return deterministic fallback or controlled `falha`.

**Independent Test**: Force parser failure in test and verify provider is called with fallback reason.

---

### P1: Prompt and response governance

**User Story**: As an avaliador tecnico, I want prompts and model decisions documented so that I can defend the AI behavior in the review.

**Why P1**: O desafio permite AI, mas exige defesa das decisoes tecnicas.

**Acceptance Criteria**:

1. WHEN AI is used THEN report SHALL include provider, model, mode, prompt version and sanitized prompt summary.
2. WHEN AI makes assumptions THEN report SHALL include those assumptions when extractable.
3. WHEN generated code is persisted THEN report SHALL include whether it came from `ai`, `deterministic`, `ai_repair` or `deterministic_fallback`.
4. WHEN credentials are present THEN system SHALL never persist API keys or secret values.

**Independent Test**: Run mocked AI and inspect report fields.

---

### P2: AI repair loop for invalid Python

**User Story**: As an implementador, I want one controlled AI repair attempt after invalid generated Python so that recoverable syntax issues do not fail the whole run.

**Why P2**: LLM output can be close but syntactically invalid; one repair attempt improves usefulness without hiding risk.

**Acceptance Criteria**:

1. WHEN AI-generated code fails `ast.parse` THEN system SHALL optionally call repair prompt once if AI is enabled.
2. WHEN repair succeeds THEN system SHALL report original validation error and repaired code validation.
3. WHEN repair fails THEN system SHALL not loop indefinitely and SHALL mark status `parcial` or `falha`.

**Independent Test**: Mock invalid first response and valid repair response.

---

### P2: Provider abstraction

**User Story**: As an implementador, I want a provider abstraction so that OpenAI, Azure OpenAI, local model or future providers can be swapped without changing graph nodes.

**Why P2**: O criterio de escalabilidade pede suporte a novos modelos.

**Acceptance Criteria**:

1. WHEN provider is selected THEN system SHALL instantiate it through a factory.
2. WHEN provider is disabled or missing config THEN factory SHALL return a no-op unavailable provider.
3. WHEN generation node uses AI THEN it SHALL depend on an interface, not provider-specific code.

**Independent Test**: Unit tests cover enabled, disabled and unavailable provider paths.

## Edge Cases

- WHEN AI returns markdown fenced code THEN system SHALL extract Python content safely.
- WHEN AI returns explanation without code THEN system SHALL mark generation failure and fallback.
- WHEN AI output imports unavailable packages THEN validation SHALL still parse, but report SHALL flag dependency assumptions if detected.
- WHEN prompt would exceed configured size budget THEN system SHALL truncate low-priority context and report truncation.
- WHEN parser fails before semantic analysis THEN AI prompt SHALL include source code and parser error at minimum.
- WHEN AI provider times out THEN system SHALL fallback deterministically and report timeout.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| AI-01 | P1: Geracao com AI quando configurada | Design | Pending |
| AI-02 | P1: AI fallback for parser/heuristic limitations | Design | Pending |
| AI-03 | P1: Prompt and response governance | Design | Pending |
| AI-04 | P2: AI repair loop for invalid Python | Design | Pending |
| AI-05 | P2: Provider abstraction | Design | Pending |

**Coverage:** 5 total, 5 mapped to design, 0 verified.

---

## Success Criteria

- [ ] Pipeline continua funcionando sem AI configurada.
- [ ] Pipeline usa provider AI mockado em testes quando configurado.
- [ ] Parser failure recuperavel aciona AI fallback.
- [ ] AI-generated code passa por `ast.parse`.
- [ ] Report identifica strategy/source: `ai`, `ai_repair`, `deterministic` ou `deterministic_fallback`.
- [ ] README documenta variaveis de ambiente, trade-offs e limites.
