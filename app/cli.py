import json
from pathlib import Path

from app.models import ValidationRequest
from app.services.guardrail import build_sample_request, evaluate_dataset


def main() -> None:
    report = evaluate_dataset(build_sample_request())

    print("Data Quality Guardrail")
    print("======================")
    print(f"Dataset: {report.dataset_name}")
    print(f"Rows analyzed: {report.rows_analyzed}")
    print(f"Overall score: {report.overall_score}")
    print()

    for finding in report.findings:
        print(f"[{finding.severity.upper()}] {finding.code} (score {finding.score})")
        print(f"Summary: {finding.summary}")
        print("Evidence:")
        for item in finding.evidence:
            print(f"  - {item}")
        print(f"Next action: {finding.recommended_next_action}")
        print()


def load_request(path: Path) -> ValidationRequest:
    with path.open("r", encoding="utf-8") as handle:
        return ValidationRequest.model_validate(json.load(handle))
