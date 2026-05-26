from typing import Any, Literal, TypedDict

PipelineStatus = Literal["sucesso", "falha", "parcial"]
GenerationStrategy = Literal["ai", "ai_repair", "deterministic", "deterministic_fallback"]


class ModernizationState(TypedDict, total=False):
    source_code: str
    schema_context: str | None
    metadata: dict[str, Any]
    parsed_representation: dict[str, Any] | None
    semantic_findings: dict[str, Any]
    generated_code: str | None
    validation: dict[str, Any]
    report: dict[str, Any]
    status: PipelineStatus
    errors: list[str]
    ai_context: dict[str, Any]
    generation_strategy: GenerationStrategy
    ai_usage: dict[str, Any]
    confidence: dict[str, Any]


def initial_state(
    source_code: str,
    schema_context: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> ModernizationState:
    return {
        "source_code": source_code,
        "schema_context": schema_context,
        "metadata": metadata or {},
        "parsed_representation": None,
        "semantic_findings": {},
        "generated_code": None,
        "validation": {},
        "report": {"stages": {}, "decisions": [], "risks": []},
        "status": "sucesso",
        "errors": [],
        "ai_context": {},
        "generation_strategy": "deterministic",
        "ai_usage": {},
        "confidence": {"parsing": 1.0, "semantic_analysis": 1.0, "reasons": []},
    }
