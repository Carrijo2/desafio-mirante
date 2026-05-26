from app.graph.state import initial_state
from app.integrations.llm import LlmPrompt, LlmResult
from app.nodes import generation


class SuccessfulProvider:
    provider = "fake"
    model = "fake-model"

    def generate(self, prompt: LlmPrompt) -> LlmResult:
        assert "Semantic findings" in prompt.text
        return LlmResult(
            available=True,
            text="```python\nfrom typing import Any\n\ndef generated() -> Any:\n    return 1\n```",
            provider=self.provider,
            model=self.model,
            usage={"input_tokens": 10},
        )

    def repair(self, prompt: LlmPrompt) -> LlmResult:
        raise AssertionError("repair should not be called")


class UnavailableProvider:
    provider = "fake"
    model = "fake-model"

    def generate(self, prompt: LlmPrompt) -> LlmResult:
        return LlmResult(
            available=False,
            provider=self.provider,
            model=self.model,
            error="not configured",
        )

    def repair(self, prompt: LlmPrompt) -> LlmResult:
        raise AssertionError("repair should not be called")


def test_generation_uses_ai_provider(monkeypatch) -> None:
    monkeypatch.setattr(generation, "get_ai_provider", lambda: SuccessfulProvider())
    state = initial_state("CREATE OR REPLACE FUNCTION fn_demo() RETURNS INT AS $$ BEGIN END; $$;")
    state["semantic_findings"] = {"routine": {"kind": "function", "name": "fn_demo"}}

    result = generation.generate_python(state)

    assert result["generation_strategy"] == "ai"
    assert "def generated" in result["generated_code"]
    assert result["report"]["stages"]["generation"]["provider"] == "fake"


def test_generation_falls_back_when_ai_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(generation, "get_ai_provider", lambda: UnavailableProvider())
    state = initial_state("CREATE OR REPLACE FUNCTION fn_demo() RETURNS INT AS $$ BEGIN END; $$;")
    state["semantic_findings"] = {"routine": {"kind": "function", "name": "fn_demo"}}
    state["confidence"] = {"parsing": 0.0, "semantic_analysis": 0.6, "reasons": ["forced"]}

    result = generation.generate_python(state)

    assert result["generation_strategy"] == "deterministic_fallback"
    assert "SOURCE_SQL" in result["generated_code"]
    assert result["report"]["stages"]["generation"]["ai_unavailable_reason"] == "not configured"

