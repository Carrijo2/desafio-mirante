from typing import Any, Literal

from pydantic import BaseModel, Field


class ModernizeRequest(BaseModel):
    source_code: str = Field(..., min_length=1)
    schema_context: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModernizeResponse(BaseModel):
    id: str | None = None
    generated_code: str | None
    report: dict[str, Any]
    status: Literal["sucesso", "falha", "parcial"]


class HealthResponse(BaseModel):
    status: str

