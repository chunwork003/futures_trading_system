"""V2 以純語意 matrix 驗證 authority boundary，不 clone Git per case。"""
from dataclasses import replace, FrozenInstanceError
import json
from pathlib import Path
import shutil
import subprocess
import pytest
from pydantic import ValidationError
from automation.engine.execution_capacity import (
    ProviderEvidence, DemandForecast, CalibrationSample, CapacityEstimate,
    ExecutionLineage, ResumeEvidence, ExecutionCheckpoint, IDENTITY_DIMENSIONS,
    qualified_samples, evaluate_admission, pause_provider_limit, provider_recovery_wake,
    evaluate_resume, route_work, ivf01_route,
)

ROOT = Path(__file__).resolve().parents[2]


def provider(**changes):
    return ProviderEvidence(**dict(dict(ordinary_usage_allowed=True, hard_block=False,
        rate_limit_denied=False, spend_control_denied=False, raw={"usedPercent": 99}), **changes))


def forecast():
    return DemandForecast(p50=100, p75=200, p90=300,
                          token_dimensions={"input": 200, "cached": 150, "uncached": 50})


def samples():
    identity = {k: k + "-fixed" for k in IDENTITY_DIMENSIONS}
    return identity, tuple(CalibrationSample(execution_id=f"E{i}", measurement_type="EXACT",
        identity=identity, token_features=dict(input_tokens=10, cached_input_tokens=6,
        uncached_input_tokens=4, output_tokens=2, reasoning_output_tokens=1, total_tokens=12),
        provider_before={"resets_at": 123, "used_percent": 1},
        provider_after={"resets_at": 123, "used_percent": 2}, exact_binding_verified=True,
        clean_attribution=True, reset_compatible=True, competing_consumer=False) for i in range(3))


def capacity():
    identity, observations = samples()
    return CapacityEstimate(measurement_type="CALIBRATED_ESTIMATE", identity=identity,
        available_tokens_lower=400, available_tokens_upper=600, feature_method="Reviewed feature model",
        uncertainty="bounded interval, same identity/window", samples=observations, qualification_reviewed=True)


def lineage():
    return ExecutionLineage(work_order_id="WO", execution_id="EXEC", authorization_id="AUTH",
        reservation_id="RES", dispatch_id="DISP", branch="auto/exact", scope_digest="digest",
        architecture_policy_identity="1.2-candidate-exact", correction_budget=0, delta_sha="sha",
        completed_tests=["targeted subset"], telemetry={"token_status": "PENDING_EXTERNAL_EXTRACTION"})


def resume():
    original = lineage()
    values = dict(original=original, current=original, authorization_state="CONSUMED",
        reservation_created=True, dispatch_committed=True, executor_invoked=True,
        invocation_evidence_verified=True, head_compatible=True, scope_compatible=True,
        architecture_policy_compatible=True, writer_owner="EXEC", writer_state="HELD",
        writer_lineage_verified=True, competing_writer=False,
        projection_phase="CURRENT_LIFECYCLE_PROJECTION", provider=provider())
    values["projection"] = {k: values[k] for k in ("authorization_state", "reservation_created",
        "dispatch_committed", "executor_invoked", "writer_owner", "writer_state")}
    values["projection"]["execution_id"] = "EXEC"
    return ExecutionCheckpoint(original, "RESUME_PENDING_REVALIDATION", 1, 0, True), values


@pytest.mark.parametrize("field,value", [("ordinary_usage_allowed", False), ("hard_block", True),
    ("rate_limit_denied", True), ("spend_control_denied", True)])
def test_provider_denial_wins(field, value):
    result = evaluate_admission(provider(**{field: value}), forecast(), capacity(),
                                exact_authorized=True, manual=True, low_risk=True)
    assert result.route == "WAIT_PROVIDER_AVAILABLE" and not result.execution_allowed


def test_no_percentage_floor_or_fallback_and_no_authority():
    assert evaluate_admission(provider(), forecast(), capacity(), exact_authorized=True,
                              manual=False, low_risk=False).route == "COST_FIT"
    result = evaluate_admission(provider(), forecast(), None, exact_authorized=True, manual=True, low_risk=True)
    assert result.route == "ALLOW_WITH_WATCH" and not result.authority_created
    assert evaluate_admission(provider(), forecast(), None, exact_authorized=True,
                              manual=False, low_risk=True).route == "WORK_CAPACITY_REVIEW"
    assert evaluate_admission(provider(), forecast(), capacity(), exact_authorized=False,
                              manual=True, low_risk=True).route == "STOP_TO_WORK"
    larger = DemandForecast(p50=100, p75=200, p90=500, token_dimensions={})
    miss = evaluate_admission(provider(), larger, capacity(), exact_authorized=True, manual=True, low_risk=True)
    assert miss.forecast_capacity_review_required and not miss.execution_allowed


@pytest.mark.parametrize("field,value", [("clean_attribution", False), ("reset_compatible", False),
    ("competing_consumer", True), ("exact_binding_verified", False),
    ("identity", {"account": "other"}), ("provider_after", {"resets_at": 456})])
def test_ambiguous_sample_never_calibrates(field, value):
    identity, observations = samples()
    changed = observations[0].model_dump()
    changed[field] = value
    altered = (CalibrationSample(**changed), *observations[1:])
    assert not qualified_samples(altered, identity)
    with pytest.raises(ValidationError):
        CapacityEstimate(measurement_type="CALIBRATED_ESTIMATE", identity=identity,
            available_tokens_lower=10, available_tokens_upper=20, feature_method="fit",
            uncertainty="interval", samples=altered, qualification_reviewed=True)


def test_estimate_never_exact_or_count_only():
    values = capacity().model_dump()
    values["measurement_type"] = "EXACT"
    with pytest.raises(ValidationError): CapacityEstimate(**values)
    values["measurement_type"] = "CALIBRATED_ESTIMATE"
    values["qualification_reviewed"] = False
    with pytest.raises(ValidationError): CapacityEstimate(**values)
    with pytest.raises(TypeError): capacity().identity["account"] = "other"


def test_pause_recovery_is_same_lineage_wake_only():
    checkpoint = ExecutionCheckpoint(lineage(), "RUNNING")
    paused = pause_provider_limit(checkpoint, provider(rate_limit_denied=True))
    assert paused.state == "PAUSED_PROVIDER_LIMIT" and paused.lineage is checkpoint.lineage
    assert paused.forecast_capacity_review_required and paused.lineage.correction_budget == 0
    wake = provider_recovery_wake(paused)
    assert wake.state == "RESUME_PENDING_REVALIDATION" and wake.lineage is checkpoint.lineage
    with pytest.raises(FrozenInstanceError): wake.state = "RUNNING"
    checkpoint, evidence = resume()
    result = evaluate_resume(checkpoint, ResumeEvidence(**evidence))
    assert result.route == "RESUME_SAME_EXECUTION" and not result.execution_allowed
    assert result.forecast_capacity_review_required


@pytest.mark.parametrize("field,value", [("authorization_state", "REVOKED"),
    ("authorization_state", "SUPERSEDED"), ("reservation_created", False),
    ("dispatch_committed", False), ("executor_invoked", False), ("invocation_evidence_verified", False),
    ("head_compatible", False), ("scope_compatible", False), ("architecture_policy_compatible", False),
    ("writer_lineage_verified", False), ("writer_owner", "OTHER"), ("writer_state", "RELEASED"),
    ("competing_writer", True)])
def test_resume_negative_matrix(field, value):
    checkpoint, evidence = resume()
    assert evaluate_resume(checkpoint, ResumeEvidence(**evidence)).route == "RESUME_SAME_EXECUTION"
    evidence[field] = value
    if field in evidence["projection"]: evidence["projection"][field] = value
    result = evaluate_resume(checkpoint, ResumeEvidence(**evidence))
    assert result.route == "STOP_TO_WORK" and not result.execution_allowed


@pytest.mark.parametrize("field", list(ExecutionLineage.model_fields))
def test_resume_no_new_identity_or_lost_progress(field):
    checkpoint, evidence = resume()
    changed = lineage().model_dump()
    changed[field] = 1 if field == "correction_budget" else ([] if field == "completed_tests" else
        {"lost": True} if field == "telemetry" else "OTHER")
    evidence["current"] = ExecutionLineage(**changed)
    evidence["projection"]["execution_id"] = evidence["current"].execution_id
    assert evaluate_resume(checkpoint, ResumeEvidence(**evidence)).route == "STOP_TO_WORK"


@pytest.mark.parametrize("field", ["reservation_created", "dispatch_committed", "executor_invoked"])
def test_contradictory_current_projection_reconciliation(field):
    checkpoint, evidence = resume()
    evidence["projection"][field] = False
    assert evaluate_resume(checkpoint, ResumeEvidence(**evidence)).route == "RECONCILIATION_REQUIRED"


def test_historical_snapshot_not_current_and_noninvoked_not_resume():
    checkpoint, evidence = resume()
    evidence["projection_phase"] = "HISTORICAL_PHASE_SNAPSHOT"
    assert evaluate_resume(checkpoint, ResumeEvidence(**evidence)).route == "RECONCILIATION_REQUIRED"
    checkpoint, evidence = resume()
    evidence["provider"] = provider(hard_block=True)
    assert evaluate_resume(checkpoint, ResumeEvidence(**evidence)).route == "WAIT_PROVIDER_AVAILABLE"


def test_resume_first_review_barriers_and_ivf_staleness():
    args = dict(safety_block=False, unfinished=True, pending_review=False,
                interrupted_completed=False, feedback_materialized=False, new_work_authorized=True)
    assert route_work(**args).route == "REENTER_UNFINISHED_EXECUTION"
    args.update(unfinished=False, interrupted_completed=True)
    assert route_work(**args).route == "WORK_FORECAST_CAPACITY_REVIEW"
    args.update(pending_review=True)
    assert route_work(**args).route == "PENDING_REVIEW_INTEGRATION"
    assert ivf01_route(active_architecture="1.1", governance_review_pass=True, activation_materialized=False).route == "BLOCKED"
    assert ivf01_route(active_architecture="1.2", governance_review_pass=True, activation_materialized=True).route == "ARCHITECTURE_BASELINE_CHANGED_RECOMPILE_REQUIRED"


@pytest.mark.parametrize("interrupted", [False, True])
def test_reconciler_backward_compatible_and_optional_pause(tmp_path, interrupted):
    forecast_doc = {"schema_version": "automation.execution_cost_forecast.v1", "confidence": "PROVISIONAL",
        "forecast": {"actor_seconds": {"p50": 10, "p75": 20, "p90": 30}}}
    actual_doc = {"schema_version": "automation.execution_cost_actual.v1", "work_order_id": "WO",
        "execution_id": "EXEC", "actual": {"actor_seconds": 10}}
    if interrupted: actual_doc["actual"].update(provider_limit_encountered=True, provider_pause_count=1,
        provider_pause_seconds=30, resume_count=1, resumed_same_execution=True)
    paths = [tmp_path / "forecast.json", tmp_path / "actual.json"]
    for path, document in zip(paths, [forecast_doc, actual_doc]): path.write_text(json.dumps(document))
    executable = shutil.which("pwsh") or shutil.which("powershell")
    assert executable, "PowerShell is required for deterministic reconciliation verification"
    result = json.loads(subprocess.check_output([executable, "-NoProfile", "-File",
        str(ROOT / "scripts/execution_cost_reconcile.ps1"), "-ForecastPath", str(paths[0]),
        "-ActualPath", str(paths[1])], encoding="utf-8-sig"))
    assert result["overall_classification"] == "NORMAL"
    assert result["dominant_cause"] == "WITHIN_EXPECTED_ENVELOPE"
    assert result["forecast_capacity_review_required"] is interrupted
    assert result["provider_pause_is_source_defect"] is False
