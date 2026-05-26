from fastapi import FastAPI, HTTPException

from app.api.schemas import HealthResponse, ModernizeRequest, ModernizeResponse
from app.graph.modernization_graph import run_modernization
from app.persistence.history_repository import save_history

app = FastAPI(title="SQL to Python Modernization Pipeline")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/modernize", response_model=ModernizeResponse)
def modernize(request: ModernizeRequest) -> ModernizeResponse:
    try:
        state = run_modernization(
            source_code=request.source_code,
            schema_context=request.schema_context,
            metadata=request.metadata,
        )
    except Exception as exc:  # pragma: no cover - defensive API boundary
        state = {
            "source_code": request.source_code,
            "generated_code": None,
            "status": "falha",
            "report": {
                "stages": {},
                "decisions": [],
                "risks": [],
                "errors": [f"graph execution failed: {exc}"],
            },
        }

    report = state.get("report", {})
    status = state.get("status", "falha")
    generated_code = state.get("generated_code")

    try:
        history_id = save_history(
            source_code=request.source_code,
            generated_code=generated_code,
            report=report,
            status=status,
        )
    except Exception as exc:
        report.setdefault("stages", {}).setdefault("persistence", {})
        report["stages"]["persistence"] = {"status": "error", "error": str(exc)}
        raise HTTPException(status_code=503, detail=report) from exc

    return ModernizeResponse(
        id=history_id,
        generated_code=generated_code,
        report=report,
        status=status,
    )

