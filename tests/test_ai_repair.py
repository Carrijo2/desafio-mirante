from app.graph.state import initial_state
from app.integrations.llm import LlmPrompt, LlmResult
from app.nodes import validation


class RepairProvider:
    provider = "fake"
    model = "fake-model"

    def generate(self, prompt: LlmPrompt) -> LlmResult:
        raise AssertionError("generate should not be called")

    def repair(self, prompt: LlmPrompt) -> LlmResult:
        return LlmResult(
            available=True,
            text="def fixed() -> int:\n    return 1\n",
            provider=self.provider,
            model=self.model,
        )


def test_validation_repairs_invalid_ai_code(monkeypatch) -> None:
    monkeypatch.setattr(validation, "get_ai_provider", lambda: RepairProvider())
    monkeypatch.setattr(validation, "is_ai_repair_enabled", lambda: True)
    state = initial_state("select 1")
    state["generated_code"] = "def broken(:\n    pass"
    state["generation_strategy"] = "ai"

    result = validation.validate_generated_code(state)

    assert result["validation"]["ast_parse"] is True
    assert result["validation"]["repair_attempted"] is True
    assert result["generation_strategy"] == "ai_repair"
    assert "def fixed" in result["generated_code"]

