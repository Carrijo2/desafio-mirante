from typing import Any

import sqlparse

from app.graph.state import ModernizationState


def _token_to_dict(token: Any) -> dict[str, Any]:
    return {
        "type": token.__class__.__name__,
        "ttype": str(getattr(token, "ttype", "")),
        "value": str(token).strip()[:200],
        "is_group": bool(getattr(token, "is_group", False)),
    }


def parse_sql(state: ModernizationState) -> ModernizationState:
    source = state.get("source_code", "")
    report = state.setdefault("report", {"stages": {}, "decisions": [], "risks": []})
    errors = state.setdefault("errors", [])
    confidence = state.setdefault(
        "confidence",
        {"parsing": 1.0, "semantic_analysis": 1.0, "reasons": []},
    )

    try:
        statements = sqlparse.parse(source)
        parsing_confidence = 0.95 if statements else 0.2
        if not statements:
            confidence.setdefault("reasons", []).append("sqlparse returned no statements.")
        parsed = {
            "parser": "sqlparse",
            "statement_count": len(statements),
            "statements": [
                {
                    "statement_type": statement.get_type(),
                    "tokens": [
                        _token_to_dict(token)
                        for token in statement.tokens
                        if str(token).strip()
                    ],
                }
                for statement in statements
            ],
        }
        state["parsed_representation"] = parsed
        confidence["parsing"] = parsing_confidence
        report["stages"]["parsing"] = {
            "status": "ok",
            "parser": "sqlparse",
            "statement_count": len(statements),
            "confidence": parsing_confidence,
            "limitations": [
                "Token-based parser; PL/pgSQL block semantics are enriched in semantic analysis."
            ],
        }
    except Exception as exc:  # pragma: no cover - defensive boundary
        state["parsed_representation"] = None
        state["status"] = "parcial"
        confidence["parsing"] = 0.0
        confidence.setdefault("reasons", []).append(f"Parser error: {exc}")
        errors.append(f"parsing: {exc}")
        report["stages"]["parsing"] = {
            "status": "error",
            "error": str(exc),
            "confidence": 0.0,
            "recoverable": True,
        }

    return state
