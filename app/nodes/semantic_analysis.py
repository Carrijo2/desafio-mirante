import re
from typing import Any

from app.graph.state import ModernizationState

PARAM_RE = re.compile(r"\b(?:IN|OUT|INOUT)?\s*(p_[a-zA-Z0-9_]+)\s+([A-Z0-9_(),]+)", re.I)
DECLARE_RE = re.compile(r"\b(v_[a-zA-Z0-9_]+)\s+([A-Z0-9_(),]+)(?:\s*:=\s*([^;]+))?;", re.I)
FUNCTION_RE = re.compile(r"CREATE\s+OR\s+REPLACE\s+(FUNCTION|PROCEDURE)\s+([a-zA-Z0-9_]+)", re.I)


def _find_parameters(source: str) -> list[dict[str, str]]:
    params: list[dict[str, str]] = []
    header_match = re.search(r"\((.*?)\)\s*(RETURNS|LANGUAGE)", source, re.I | re.S)
    if not header_match:
        return params
    for raw_param in header_match.group(1).split(","):
        match = PARAM_RE.search(raw_param.strip())
        if match:
            direction_match = re.match(r"\s*(INOUT|IN|OUT)\b", raw_param, re.I)
            params.append(
                {
                    "name": match.group(1),
                    "type": match.group(2),
                    "direction": direction_match.group(1).upper() if direction_match else "IN",
                }
            )
    return params


def _find_variables(source: str) -> list[dict[str, str | None]]:
    return [
        {"name": name, "type": var_type, "default": default.strip() if default else None}
        for name, var_type, default in DECLARE_RE.findall(source)
    ]


def _presence(source_upper: str, patterns: dict[str, str]) -> dict[str, bool]:
    return {
        name: bool(re.search(pattern, source_upper, re.S))
        for name, pattern in patterns.items()
    }


def analyze_semantics(state: ModernizationState) -> ModernizationState:
    source = state.get("source_code", "")
    source_upper = source.upper()
    report = state.setdefault("report", {"stages": {}, "decisions": [], "risks": []})
    confidence = state.setdefault(
        "confidence",
        {"parsing": 1.0, "semantic_analysis": 1.0, "reasons": []},
    )

    routine_match = FUNCTION_RE.search(source)
    constructs: dict[str, Any] = _presence(
        source_upper,
        {
            "cursor": r"\bCURSOR\b|\bOPEN\b|\bFETCH\b|\bCLOSE\b",
            "exception_block": r"\bEXCEPTION\b",
            "raise": r"\bRAISE\b",
            "cte": r"\bWITH\s+RECURSIVE\b|\bWITH\b",
            "recursive_cte": r"\bWITH\s+RECURSIVE\b",
            "jsonb": r"\bJSONB\b|JSONB_BUILD_OBJECT",
            "for_update": r"\bFOR\s+UPDATE\b",
            "return_query": r"\bRETURN\s+QUERY\b",
            "get_diagnostics": r"\bGET\s+DIAGNOSTICS\b",
            "transactional_writes": r"\bUPDATE\b|\bINSERT\b|\bDELETE\b",
            "nested_fn_saldo_cliente": r"\bFN_SALDO_CLIENTE\s*\(",
        },
    )
    constructs["parameters"] = _find_parameters(source)
    constructs["variables"] = _find_variables(source)
    constructs["routine"] = {
        "kind": routine_match.group(1).lower() if routine_match else "unknown",
        "name": routine_match.group(2) if routine_match else "unknown",
    }

    risks: list[str] = []
    semantic_confidence = 0.95
    if constructs["routine"]["name"] == "unknown":
        semantic_confidence = 0.45
        confidence.setdefault("reasons", []).append("Routine name could not be detected.")
    if not constructs["parameters"] and "(" in source and ")" in source:
        semantic_confidence = min(semantic_confidence, 0.7)
        confidence.setdefault("reasons", []).append("Routine parameters could not be detected.")
    if constructs["cursor"]:
        risks.append("Explicit cursor may translate to N+1 queries if implemented naively.")
    if constructs["for_update"]:
        risks.append("FOR UPDATE requires preserving locking and transaction semantics.")
    if constructs["raise"]:
        risks.append("RAISE statements need Python exception/logging mapping.")
    if constructs["jsonb"]:
        risks.append("JSONB construction needs Python dict or SQL delegation decision.")
    if constructs["recursive_cte"]:
        risks.append("Recursive CTE should likely stay delegated to PostgreSQL.")
    if constructs["exception_block"]:
        risks.append("Exception blocks need fallback or audit behavior in Python.")

    state["semantic_findings"] = constructs
    confidence["semantic_analysis"] = semantic_confidence
    report["stages"]["semantic_analysis"] = {
        "status": "ok",
        "routine": constructs["routine"],
        "parameters": constructs["parameters"],
        "variables": constructs["variables"],
        "constructs": {key: value for key, value in constructs.items() if isinstance(value, bool)},
        "risks": risks,
        "confidence": semantic_confidence,
    }
    report["risks"] = list(dict.fromkeys([*report.get("risks", []), *risks]))
    return state
