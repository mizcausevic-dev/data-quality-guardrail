from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RangeRule(BaseModel):
    min: float
    max: float


class ValidationRequest(BaseModel):
    dataset_name: str
    generated_at: datetime
    allowed_freshness_minutes: int = Field(gt=0)
    required_columns: list[str]
    range_rules: dict[str, RangeRule]
    records: list[dict[str, Any]]


class Finding(BaseModel):
    code: str
    severity: str
    score: int
    summary: str
    evidence: list[str]
    recommended_next_action: str


class ValidationReport(BaseModel):
    dataset_name: str
    rows_analyzed: int
    overall_score: int
    evaluated_at: datetime
    findings: list[Finding]


class HealthResponse(BaseModel):
    status: str
    service: str
    docs: str
    sample_dataset: str
