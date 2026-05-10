import json
from datetime import UTC, datetime
from pathlib import Path

from app.models import Finding, ValidationReport, ValidationRequest

SAMPLE_DATA_PATH = Path("data/sample_pipeline_snapshot.json")


def build_sample_request() -> ValidationRequest:
    with SAMPLE_DATA_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return ValidationRequest.model_validate(payload)


def evaluate_dataset(request: ValidationRequest) -> ValidationReport:
    findings: list[Finding] = []

    schema = schema_drift(request)
    if schema:
        findings.append(schema)

    freshness = freshness_lag(request)
    if freshness:
        findings.append(freshness)

    nulls = null_spike(request)
    if nulls:
        findings.append(nulls)

    duplicates = duplicate_collision(request)
    if duplicates:
        findings.append(duplicates)

    ranges = range_violation(request)
    if ranges:
        findings.append(ranges)

    overall_score = max((finding.score for finding in findings), default=12)

    return ValidationReport(
        dataset_name=request.dataset_name,
        rows_analyzed=len(request.records),
        overall_score=overall_score,
        evaluated_at=datetime.now(UTC),
        findings=findings,
    )


def schema_drift(request: ValidationRequest) -> Finding | None:
    expected = set(request.required_columns)
    missing_counts: dict[str, int] = {column: 0 for column in request.required_columns}
    unexpected_columns: set[str] = set()

    for record in request.records:
        for column in expected:
            if column not in record:
                missing_counts[column] += 1
        unexpected_columns.update(set(record.keys()) - expected)

    evidence: list[str] = []

    for column, count in missing_counts.items():
        if count > 0:
            evidence.append(f"{column} missing from {count} row(s)")

    if unexpected_columns:
        evidence.append("unexpected fields present: " + ", ".join(sorted(unexpected_columns)))

    if not evidence:
        return None

    return Finding(
        code="schema_drift",
        severity="moderate",
        score=71,
        summary="Dataset shape is drifting away from the expected contract.",
        evidence=evidence,
        recommended_next_action="Lock the contract, remove unexpected fields, and backfill missing required columns before the next reporting cut.",
    )


def freshness_lag(request: ValidationRequest) -> Finding | None:
    age_minutes = int((datetime.now(UTC) - request.generated_at).total_seconds() / 60)
    if age_minutes <= request.allowed_freshness_minutes:
        return None

    return Finding(
        code="freshness_lag",
        severity="critical",
        score=89,
        summary="Dataset freshness is materially outside the allowed reporting window.",
        evidence=[
            f"generated_at is {age_minutes} minute(s) old",
            f"allowed freshness window is {request.allowed_freshness_minutes} minute(s)",
        ],
        recommended_next_action="Restore the ingestion schedule and halt downstream decisioning that assumes current-state data.",
    )


def null_spike(request: ValidationRequest) -> Finding | None:
    critical_fields = ["account_id", "opportunity_id", "owner_email"]
    evidence: list[str] = []

    for field in critical_fields:
        count = sum(1 for row in request.records if row.get(field) in (None, ""))
        if count:
            evidence.append(f"{field} is null in {count} row(s)")

    if not evidence:
        return None

    return Finding(
        code="null_spike",
        severity="moderate",
        score=66,
        summary="Critical fields are missing often enough to degrade routing and reporting quality.",
        evidence=evidence,
        recommended_next_action="Backfill missing identifiers and block the feed from downstream enrichment until completeness recovers.",
    )


def duplicate_collision(request: ValidationRequest) -> Finding | None:
    seen: set[str] = set()
    duplicates: list[str] = []

    for row in request.records:
        key = str(row.get("snapshot_id"))
        if key in seen:
            duplicates.append(key)
        seen.add(key)

    if not duplicates:
        return None

    return Finding(
        code="duplicate_collision",
        severity="high",
        score=78,
        summary="Primary snapshot keys are repeating and can inflate downstream metrics.",
        evidence=[f"duplicate snapshot_id values: {', '.join(duplicates)}"],
        recommended_next_action="Deduplicate the batch and verify the export process is not replaying already-published rows.",
    )


def range_violation(request: ValidationRequest) -> Finding | None:
    evidence: list[str] = []

    for field, rule in request.range_rules.items():
        for index, row in enumerate(request.records, start=1):
            value = row.get(field)
            if value is None:
                continue
            if value < rule.min or value > rule.max:
                evidence.append(
                    f"row {index} has {field}={value} outside [{rule.min}, {rule.max}]"
                )

    if not evidence:
        return None

    return Finding(
        code="range_violation",
        severity="high",
        score=81,
        summary="Numeric values are exceeding guardrail ranges strongly enough to distort trusted reporting.",
        evidence=evidence,
        recommended_next_action="Quarantine outlier rows, confirm business-rule thresholds, and stop these values from entering executive rollups.",
    )
