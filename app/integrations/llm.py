import os
import re
from dataclasses import dataclass, field
from typing import Any, Protocol

from app.graph.state import ModernizationState

PROMPT_VERSION = "sql-to-python-modernization-v1"


@dataclass(frozen=True)
class LlmPrompt:
    version: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LlmResult:
    available: bool
    text: str = ""
    provider: str = "disabled"
    model: str | None = None
    usage: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class LlmProvider(Protocol):
    provider: str
    model: str | None

    def generate(self, prompt: LlmPrompt) -> LlmResult:
        """Generate modernization code."""

    def repair(self, prompt: LlmPrompt) -> LlmResult:
        """Repair invalid Python code."""


class UnavailableLlmProvider:
    def __init__(self, reason: str, provider: str = "disabled", model: str | None = None) -> None:
        self.reason = reason
        self.provider = provider
        self.model = model

    def generate(self, prompt: LlmPrompt) -> LlmResult:
        return LlmResult(
            available=False,
            provider=self.provider,
            model=self.model,
            error=self.reason,
        )

    def repair(self, prompt: LlmPrompt) -> LlmResult:
        return self.generate(prompt)


class OpenAiResponsesProvider:
    def __init__(self, model: str, timeout_seconds: float) -> None:
        from openai import OpenAI

        self.provider = "openai"
        self.model = model
        self._client = OpenAI(timeout=timeout_seconds)

    def generate(self, prompt: LlmPrompt) -> LlmResult:
        return self._create(prompt)

    def repair(self, prompt: LlmPrompt) -> LlmResult:
        return self._create(prompt)

    def _create(self, prompt: LlmPrompt) -> LlmResult:
        try:
            response = self._client.responses.create(
                model=self.model,
                instructions=(
                    "You are a senior Python modernization engineer. "
                    "Return only valid Python 3.14 code. Do not include prose."
                ),
                input=prompt.text,
            )
            usage = getattr(response, "usage", None)
            usage_dict = usage.model_dump(mode="json") if hasattr(usage, "model_dump") else {}
            return LlmResult(
                available=True,
                text=response.output_text,
                provider=self.provider,
                model=self.model,
                usage=usage_dict,
            )
        except Exception as exc:  # pragma: no cover - network/provider boundary
            return LlmResult(
                available=False,
                provider=self.provider,
                model=self.model,
                error=str(exc),
            )


def get_ai_provider() -> LlmProvider:
    provider = os.getenv("AI_PROVIDER", "disabled").strip().lower()
    model = os.getenv("AI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"
    timeout = float(os.getenv("AI_TIMEOUT_SECONDS", "60"))

    if provider in {"", "disabled", "none", "off"}:
        return UnavailableLlmProvider("AI_PROVIDER is disabled.", provider="disabled", model=model)

    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            return UnavailableLlmProvider(
                "OPENAI_API_KEY is not configured.",
                provider="openai",
                model=model,
            )
        return OpenAiResponsesProvider(model=model, timeout_seconds=timeout)

    return UnavailableLlmProvider(
        f"Unsupported AI_PROVIDER: {provider}",
        provider=provider,
        model=model,
    )


def is_ai_repair_enabled() -> bool:
    return os.getenv("AI_REPAIR_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}


def build_generation_context(state: ModernizationState) -> dict[str, object]:
    """Build the model context from prior deterministic stages."""
    return {
        "source_code": state.get("source_code", ""),
        "schema_context": state.get("schema_context"),
        "parsed_representation": state.get("parsed_representation"),
        "semantic_findings": state.get("semantic_findings", {}),
        "confidence": state.get("confidence", {}),
        "errors": state.get("errors", []),
    }


def build_generation_prompt(state: ModernizationState) -> LlmPrompt:
    context = build_generation_context(state)
    semantic_findings = context["semantic_findings"]
    confidence = context["confidence"]

    text = f"""
Modernize the following PL/pgSQL routine to a Python 3.14 module.

Rules:
- Return only Python code.
- Use typed function signatures where practical.
- Prefer explicit SQL delegation for transactional logic, recursive CTEs, cursors, FOR UPDATE,
  JSONB-heavy expressions, or behavior that is risky to rewrite.
- If using SQL delegation, keep the SQL auditable and parameter handling clear.
- Include comments only where they explain a non-obvious migration decision.
- Do not invent unavailable dependencies.

Schema context:
{context.get("schema_context") or "[not provided]"}

Parser and confidence context:
{confidence}

Semantic findings:
{semantic_findings}

Parser representation summary:
{context.get("parsed_representation")}

Source PL/pgSQL:
```sql
{context.get("source_code")}
```
""".strip()

    return LlmPrompt(
        version=PROMPT_VERSION,
        text=text,
        metadata={
            "prompt_version": PROMPT_VERSION,
            "has_schema_context": bool(context.get("schema_context")),
            "confidence": confidence,
        },
    )


def build_repair_prompt(code: str, error: str) -> LlmPrompt:
    text = f"""
Repair this Python 3.14 module so that it passes ast.parse.
Return only the repaired Python code.

Syntax error:
{error}

Invalid Python:
```python
{code}
```
""".strip()
    return LlmPrompt(
        version=f"{PROMPT_VERSION}-repair",
        text=text,
        metadata={"prompt_version": f"{PROMPT_VERSION}-repair"},
    )


def extract_python_code(text: str) -> str:
    fenced = re.search(r"```(?:python|py)?\s*(.*?)```", text, flags=re.I | re.S)
    if fenced:
        return fenced.group(1).strip()
    return text.strip()


def prompt_summary(prompt: LlmPrompt) -> dict[str, Any]:
    return {
        "version": prompt.version,
        "length": len(prompt.text),
        "metadata": prompt.metadata,
    }
