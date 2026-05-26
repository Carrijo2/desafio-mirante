from app.graph.state import initial_state
from app.integrations.llm import (
    LlmPrompt,
    LlmResult,
    build_generation_prompt,
    extract_python_code,
    get_ai_provider,
)


def test_get_ai_provider_disabled(monkeypatch) -> None:
    monkeypatch.setenv("AI_PROVIDER", "disabled")

    provider = get_ai_provider()
    result = provider.generate(LlmPrompt(version="test", text="prompt"))

    assert result.available is False
    assert result.provider == "disabled"


def test_get_ai_provider_openai_without_key(monkeypatch) -> None:
    monkeypatch.setenv("AI_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    provider = get_ai_provider()
    result = provider.generate(LlmPrompt(version="test", text="prompt"))

    assert result.available is False
    assert "OPENAI_API_KEY" in result.error


def test_extract_python_code_from_fence() -> None:
    raw = "Some text\n```python\nprint('ok')\n```\n"

    assert extract_python_code(raw) == "print('ok')"


def test_generation_prompt_includes_structured_context() -> None:
    state = initial_state("CREATE OR REPLACE FUNCTION fn_demo() RETURNS INT AS $$ BEGIN END; $$;")
    state["parsed_representation"] = {"parser": "sqlparse"}
    state["semantic_findings"] = {"routine": {"name": "fn_demo"}}

    prompt = build_generation_prompt(state)

    assert "parsed" in prompt.text.lower() or "Parser representation" in prompt.text
    assert "fn_demo" in prompt.text
    assert prompt.version


class FakeProvider:
    provider = "fake"
    model = "fake-model"

    def generate(self, prompt: LlmPrompt) -> LlmResult:
        return LlmResult(
            available=True,
            text="```python\nVALUE = 1\n```",
            provider=self.provider,
            model=self.model,
        )

    def repair(self, prompt: LlmPrompt) -> LlmResult:
        return LlmResult(
            available=True,
            text="VALUE = 2",
            provider=self.provider,
            model=self.model,
        )

