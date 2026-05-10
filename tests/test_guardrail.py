from app.services.guardrail import build_sample_request, evaluate_dataset


def test_sample_request_loads():
    request = build_sample_request()
    assert request.dataset_name == "revops_pipeline_snapshot"
    assert len(request.records) == 12


def test_guardrail_finds_multiple_issue_families():
    report = evaluate_dataset(build_sample_request())
    codes = {finding.code for finding in report.findings}
    assert report.overall_score >= 80
    assert "freshness_lag" in codes
    assert "duplicate_collision" in codes
    assert "range_violation" in codes
