import ast

from app.graph.state import ModernizationState
from app.integrations.llm import (
    build_repair_prompt,
    extract_python_code,
    get_ai_provider,
    is_ai_repair_enabled,
    prompt_summary,
)


def _try_parse(code: str) -> tuple[bool, str | None]:
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as exc:
        return False, f"{exc.msg} at line {exc.lineno}"


def validate_generated_code(state: ModernizationState) -> ModernizationState:
    code = state.get("generated_code") or ""
    report = state.setdefault("report", {"stages": {}, "decisions": [], "risks": []})
    validation: dict[str, object] = {"ast_parse": False, "errors": [], "repair_attempted": False}

    if not code.strip():
        validation["errors"].append("No generated code to validate.")  # type: ignore[attr-defined]
        state["status"] = "falha"
    else:
        parsed, parse_error = _try_parse(code)
        if parsed:
            validation["ast_parse"] = True
        else:
            validation["errors"].append(parse_error)  # type: ignore[attr-defined]
            strategy = state.get("generation_strategy")
            if strategy == "ai" and is_ai_repair_enabled():
                provider = get_ai_provider()
                prompt = build_repair_prompt(code=code, error=parse_error or "unknown syntax error")
                repair_result = provider.repair(prompt)
                validation["repair_attempted"] = True
                validation["repair"] = {
                    "provider": repair_result.provider,
                    "model": repair_result.model,
                    "available": repair_result.available,
                    "error": repair_result.error,
                    "prompt": prompt_summary(prompt),
                    "usage": repair_result.usage,
                }
                if repair_result.available and repair_result.text.strip():
                    repaired_code = extract_python_code(repair_result.text)
                    repaired_ok, repaired_error = _try_parse(repaired_code)
                    if repaired_ok:
                        state["generated_code"] = repaired_code
                        state["generation_strategy"] = "ai_repair"
                        validation["ast_parse"] = True
                        validation["repair_succeeded"] = True
                    else:
                        validation["repair_succeeded"] = False
                        validation["repair_error"] = repaired_error
            if not validation["ast_parse"]:
                state["status"] = "falha"

    if state.get("status") == "sucesso" and validation["errors"]:
        state["status"] = "parcial"

    state["validation"] = validation
    report["stages"]["validation"] = {
        "status": "ok" if validation["ast_parse"] else "error",
        **validation,
    }
    return state
