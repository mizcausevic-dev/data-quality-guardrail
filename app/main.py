from pathlib import Path

from fastapi import FastAPI

from app.models import HealthResponse, ValidationRequest
from app.services.guardrail import build_sample_request, evaluate_dataset

app = FastAPI(
    title="Data Quality Guardrail",
    version="0.1.0",
    description="Dataset validation backend for schema drift, freshness, null, duplicate, and range checks.",
)


@app.get("/", response_model=HealthResponse)
def root() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="data-quality-guardrail",
        docs="/docs",
        sample_dataset=str(Path("data/sample_pipeline_snapshot.json")),
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="data-quality-guardrail",
        docs="/docs",
        sample_dataset=str(Path("data/sample_pipeline_snapshot.json")),
    )


@app.get("/api/sample")
def sample_validation():
    return evaluate_dataset(build_sample_request())


@app.post("/api/validate")
def validate_dataset(request: ValidationRequest):
    return evaluate_dataset(request)
