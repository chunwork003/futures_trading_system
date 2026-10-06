"""V2 以純語意 matrix 驗證 authority boundary，不 clone Git per case。"""
from dataclasses import replace, FrozenInstanceError
import json
from pathlib import Path
import shutil
import subprocess
import warnings
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
        provider_before={"resets_at": 123, "used_percent": 1,
                         **{key: identity[key] for key in ("provider", "limit_id", "window_type", "account", "workspace")}},
        provider_after={"resets_at": 123, "used_percent": 2,
                        **{key: identity[key] for key in ("provider", "limit_id", "window_type", "account", "workspace")}}, exact_binding_verified=True,
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


def test_rf01_cal_minimum_counterexample():
    identity, observations = samples()
    changed = observations[0].model_dump()
    changed["token_features"] = dict(changed["token_features"], reasoning_output_tokens=3)
    assert not qualified_samples((CalibrationSample(**changed), *observations[1:]), identity)


def test_rf01_ser_minimum_counterexample():
    original = capacity()
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        dumped = original.model_dump()
        encoded = original.model_dump_json()
    assert not captured
    assert type(dumped["identity"]) is dict
    assert CapacityEstimate.model_validate_json(encoded) == original


@pytest.mark.parametrize("field,value", [("reasoning_output_tokens", 3), ("total_tokens", 13),
    ("cached_input_tokens", 7), ("uncached_input_tokens", 5),
    *[(key, value) for key in ("input_tokens", "cached_input_tokens", "uncached_input_tokens",
        "output_tokens", "reasoning_output_tokens", "total_tokens") for value in (-1, 1.5, True, "1")]])
def test_rf01_complete_token_accounting(field, value):
    identity, observations = samples()
    assert qualified_samples(observations, identity)
    changed = observations[0].model_dump()
    changed["token_features"][field] = value
    assert not qualified_samples((CalibrationSample(**changed), *observations[1:]), identity)


@pytest.mark.parametrize("window", ["provider_before", "provider_after"])
@pytest.mark.parametrize("key", ["provider", "limit_id", "window_type", "account", "workspace",
                                 "model", "executor_profile", "provider_client_policy_version"])
def test_rf01_provider_window_identity(window, key):
    identity, observations = samples()
    assert qualified_samples(observations, identity)
    changed = observations[0].model_dump()
    changed[window][key] = "OTHER"
    assert not qualified_samples((CalibrationSample(**changed), *observations[1:]), identity)


@pytest.mark.parametrize("key", ["provider", "limit_id", "window_type", "resets_at", "used_percent"])
@pytest.mark.parametrize("window", ["provider_before", "provider_after"])
def test_rf01_missing_required_provider_facts(window, key):
    identity, observations = samples()
    changed = observations[0].model_dump()
    del changed[window][key]
    assert not qualified_samples((CalibrationSample(**changed), *observations[1:]), identity)


@pytest.mark.parametrize("key", ["account", "workspace"])
def test_rf01_optional_identity_not_fabricated(key):
    identity, observations = samples()
    # 身分未由 provider snapshot 表示時不補造；任一端表示後必須雙端相符。
    changed = [item.model_dump() for item in observations]
    for item in changed:
        for window in ("provider_before", "provider_after"):
            del item[window][key]
    absent = tuple(CalibrationSample(**item) for item in changed)
    assert qualified_samples(absent, identity)
    changed[0]["provider_before"][key] = identity[key]
    assert not qualified_samples(tuple(CalibrationSample(**item) for item in changed), identity)


@pytest.mark.parametrize("after", [None, 120, -1, True, "60"])
def test_rf01_window_duration_incompatibility(after):
    identity, observations = samples()
    changed = observations[0].model_dump()
    changed["provider_before"]["window_duration_mins"] = 60
    changed["provider_after"]["window_duration_mins"] = after
    assert not qualified_samples((CalibrationSample(**changed), *observations[1:]), identity)


def test_rf01_clean_sample_positive_and_dump_roundtrip():
    identity, observations = samples()
    assert qualified_samples(observations, identity)
    original = capacity()
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        first = original.model_dump()
        second = original.model_dump()
        encoded = original.model_dump_json()
        restored = CapacityEstimate.model_validate_json(encoded)
        restored_from_plain = CapacityEstimate.model_validate(first)
    assert captured == []
    assert first == second == json.loads(encoded) == restored.model_dump()
    assert restored_from_plain == restored == original
    assert type(first["samples"]) is list and type(first["samples"][0]["token_features"]) is dict
    first["samples"][0]["token_features"]["total_tokens"] = -1
    assert original.samples[0].token_features["total_tokens"] == 12
    with pytest.raises(TypeError): original.samples[0].token_features["total_tokens"] = -1


# ---------------------------------------------------------------------------
# Policy 2.2 rolling estimator / admission
# ---------------------------------------------------------------------------


def rolling_observation(
    execution_id: str,
    *,
    ratio_tokens: int = 1000,
    before: float = 10,
    after: float = 11,
    reset_before: str = "R1",
    reset_after: str = "R1",
    actor_end_utc: str | None = None,
    window_type: str = "PRIMARY_5H",
    provider_name: str = "openai",
    account: str = "acct",
    limit_id: str = "limit",
    overlapping_usage: bool = False,
    metadata: dict | None = None,
):
    from automation.engine.execution_capacity import RollingCapacityObservation

    return RollingCapacityObservation(
        execution_id=execution_id,
        actor_end_utc=actor_end_utc or f"2026-10-06T00:{int(execution_id[1:]) % 60:02d}:00Z",
        provider=provider_name,
        account=account,
        limit_id=limit_id,
        window_type=window_type,
        exact_total_tokens=ratio_tokens,
        before_used_percent=before,
        after_used_percent=after,
        before_reset=reset_before,
        after_reset=reset_after,
        exact_binding_verified=True,
        overlapping_usage=overlapping_usage,
        metadata=metadata or {},
    )


def test_policy22_pool_identity_ignores_metadata_dimensions():
    from automation.engine.execution_capacity import estimate_rolling_capacity

    observations = (
        rolling_observation("E1", ratio_tokens=1000, metadata={"model": "A", "workspace": "W1"}),
        rolling_observation("E2", ratio_tokens=800, metadata={"model": "B", "workspace": "W2"}),
    )
    estimate = estimate_rolling_capacity(
        observations,
        provider="openai",
        account="acct",
        limit_id="limit",
        window_type="PRIMARY_5H",
        current_used_percent=50,
    )

    assert estimate.usable_ratio_count == 2
    assert estimate.safe_tokens_per_percentage_point == 800
    assert estimate.safe_remaining_percentage_points == 49
    assert estimate.safe_available_tokens == 39200


def test_policy22_count_1_to_4_uses_minimum():
    from automation.engine.execution_capacity import estimate_rolling_capacity

    observations = tuple(
        rolling_observation(f"E{i}", ratio_tokens=value)
        for i, value in enumerate((1000, 700, 900, 800), start=1)
    )
    estimate = estimate_rolling_capacity(
        observations,
        provider="openai",
        account="acct",
        limit_id="limit",
        window_type="PRIMARY_5H",
        current_used_percent=10,
    )
    assert estimate.safe_tokens_per_percentage_point == 700
    assert estimate.confidence == "MINIMUM_1_TO_4"


def test_policy22_count_5_plus_uses_linear_p25():
    from automation.engine.execution_capacity import estimate_rolling_capacity

    observations = tuple(
        rolling_observation(f"E{i}", ratio_tokens=value)
        for i, value in enumerate((100, 200, 300, 400, 500), start=1)
    )
    estimate = estimate_rolling_capacity(
        observations,
        provider="openai",
        account="acct",
        limit_id="limit",
        window_type="PRIMARY_5H",
        current_used_percent=0,
    )
    assert estimate.safe_tokens_per_percentage_point == 200
    assert estimate.confidence == "P25_5_PLUS"
    assert estimate.safe_remaining_percentage_points == 99


def test_policy22_last20_usable_ratios_only():
    from automation.engine.execution_capacity import estimate_rolling_capacity

    observations = tuple(
        rolling_observation(
            f"E{i}",
            ratio_tokens=i * 100,
            actor_end_utc=f"2026-10-06T{i:02d}:00:00Z",
        )
        for i in range(1, 26)
    )
    estimate = estimate_rolling_capacity(
        observations,
        provider="openai",
        account="acct",
        limit_id="limit",
        window_type="PRIMARY_5H",
        current_used_percent=50,
    )

    assert estimate.usable_ratio_count == 20
    assert estimate.considered_execution_ids[0] == "E6"
    assert estimate.considered_execution_ids[-1] == "E25"


def test_policy22_delta_zero_and_reset_crossing_excluded_from_ratio():
    from automation.engine.execution_capacity import estimate_rolling_capacity

    observations = (
        rolling_observation("E1", before=10, after=10),
        rolling_observation("E2", reset_before="R1", reset_after="R2"),
    )
    estimate = estimate_rolling_capacity(
        observations,
        provider="openai",
        account="acct",
        limit_id="limit",
        window_type="PRIMARY_5H",
        current_used_percent=30,
    )
    assert estimate.usable_ratio_count == 0
    assert estimate.safe_available_tokens is None
    assert estimate.confidence == "UNKNOWN"


def test_policy22_overlap_ratio_retained_but_flagged_noisy():
    from automation.engine.execution_capacity import estimate_rolling_capacity

    estimate = estimate_rolling_capacity(
        (rolling_observation("E1", overlapping_usage=True),),
        provider="openai",
        account="acct",
        limit_id="limit",
        window_type="PRIMARY_5H",
        current_used_percent=25,
    )
    assert estimate.usable_ratio_count == 1
    assert estimate.overlap_observed is True


def test_policy22_manual_uses_p75_and_weekly_never_blocks():
    from automation.engine.execution_capacity import (
        RollingCapacityEstimate,
        evaluate_policy_2_2_admission,
    )

    primary = RollingCapacityEstimate(
        "ROLLING_CAPACITY_ESTIMATE", "PRIMARY_5H", 5, ("E1",),
        100.0, 50.0, 250, "P25_5_PLUS", False,
    )
    weekly = RollingCapacityEstimate(
        "ROLLING_CAPACITY_ESTIMATE", "SECONDARY_WEEKLY", 5, ("W1",),
        1.0, 1.0, 1, "P25_5_PLUS", False,
    )

    result = evaluate_policy_2_2_admission(
        provider(),
        forecast(),
        primary,
        weekly,
        exact_authorized=True,
        dispatch_mode="MANUAL",
    )
    assert result.route == "ALLOW_WITH_WATCH"


def test_policy22_manual_below_p75_waits_and_unknown_allows_watch():
    from automation.engine.execution_capacity import (
        RollingCapacityEstimate,
        evaluate_policy_2_2_admission,
    )

    low = RollingCapacityEstimate(
        "ROLLING_CAPACITY_ESTIMATE", "PRIMARY_5H", 1, ("E1",),
        100.0, 1.0, 199, "MINIMUM_1_TO_4", False,
    )
    assert evaluate_policy_2_2_admission(
        provider(), forecast(), low, None,
        exact_authorized=True, dispatch_mode="MANUAL",
    ).route == "WAIT_5H_CAPACITY"

    assert evaluate_policy_2_2_admission(
        provider(), forecast(), None, None,
        exact_authorized=True, dispatch_mode="MANUAL",
    ).route == "ALLOW_WITH_WATCH"


def test_policy22_controlled_auto_requires_p90_and_promotion():
    from automation.engine.execution_capacity import (
        RollingCapacityEstimate,
        evaluate_policy_2_2_admission,
    )

    fit = RollingCapacityEstimate(
        "ROLLING_CAPACITY_ESTIMATE", "PRIMARY_5H", 5, ("E1",),
        100.0, 50.0, 300, "P25_5_PLUS", False,
    )

    assert evaluate_policy_2_2_admission(
        provider(), forecast(), fit, None,
        exact_authorized=True,
        dispatch_mode="CONTROLLED_AUTO",
        controlled_auto_promotion_ready=False,
    ).route == "CONTROLLED_AUTO_PROMOTION_REQUIRED"

    assert evaluate_policy_2_2_admission(
        provider(), forecast(), fit, None,
        exact_authorized=True,
        dispatch_mode="CONTROLLED_AUTO",
        controlled_auto_promotion_ready=True,
    ).route == "CONTROLLED_AUTO_CAPACITY_FIT"


def test_policy22_provider_denial_wins_for_codex():
    from automation.engine.execution_capacity import evaluate_policy_2_2_admission

    result = evaluate_policy_2_2_admission(
        provider(hard_block=True),
        forecast(),
        None,
        None,
        exact_authorized=True,
        dispatch_mode="MANUAL",
        executor_mode="CODEX",
    )
    assert result.route == "WAIT_PROVIDER_AVAILABLE"


def test_policy22_human_dialogue_capacity_gate_not_applicable():
    from automation.engine.execution_capacity import evaluate_policy_2_2_admission

    result = evaluate_policy_2_2_admission(
        provider(hard_block=True),
        forecast(),
        None,
        None,
        exact_authorized=True,
        dispatch_mode="MANUAL",
        executor_mode="HUMAN_DIALOGUE",
    )
    assert result.route == "ALLOW_WITH_WATCH"
    assert result.reason == "HUMAN_DIALOGUE_CODEX_CAPACITY_GATE_NOT_APPLICABLE"


def test_policy22_liveness_requires_complete_primary_window_and_reset():
    from automation.engine.execution_capacity import (
        CapacityLivenessEvidence,
        evaluate_capacity_liveness,
    )

    good = CapacityLivenessEvidence(
        only_blocker="WAIT_5H_CAPACITY",
        blocked_minutes=300,
        window_type="PRIMARY_5H",
        primary_window_minutes=300,
        reset_boundary_crossed=True,
        provider_continuously_available=True,
        actual_denial_observed=False,
        unchanged_work_scope_authority=True,
        authorized_ready_and_noncapacity_gates_pass=True,
    )
    assert evaluate_capacity_liveness(good).route == "CAPACITY_LIVENESS_OPTIMIZATION"

    short = replace(good, blocked_minutes=299)
    assert evaluate_capacity_liveness(short).route == "NO_CAPACITY_LIVENESS_ACTION"

    denied = replace(good, actual_denial_observed=True)
    assert evaluate_capacity_liveness(denied).route == "NO_CAPACITY_LIVENESS_ACTION"



def test_policy22_secondary_weekly_cannot_be_used_as_primary_gate():
    from automation.engine.execution_capacity import (
        RollingCapacityEstimate,
        evaluate_policy_2_2_admission,
    )

    weekly_disguised_as_primary = RollingCapacityEstimate(
        "ROLLING_CAPACITY_ESTIMATE",
        "SECONDARY_WEEKLY",
        5,
        ("W1",),
        1.0,
        1.0,
        1,
        "P25_5_PLUS",
        False,
    )

    manual = evaluate_policy_2_2_admission(
        provider(), forecast(), weekly_disguised_as_primary, None,
        exact_authorized=True, dispatch_mode="MANUAL",
    )
    assert manual.route == "ALLOW_WITH_WATCH"
    assert manual.reason == "PRIMARY_5H_UNKNOWN_MANUAL"

    controlled = evaluate_policy_2_2_admission(
        provider(), forecast(), weekly_disguised_as_primary, None,
        exact_authorized=True,
        dispatch_mode="CONTROLLED_AUTO",
        controlled_auto_promotion_ready=True,
    )
    assert controlled.route == "CONTROLLED_AUTO_CAPACITY_NOT_ESTABLISHED"


def test_policy22_liveness_requires_authorized_ready_noncapacity_pass():
    from automation.engine.execution_capacity import (
        CapacityLivenessEvidence,
        evaluate_capacity_liveness,
    )

    evidence = CapacityLivenessEvidence(
        only_blocker="WAIT_5H_CAPACITY",
        blocked_minutes=300,
        window_type="PRIMARY_5H",
        primary_window_minutes=300,
        reset_boundary_crossed=True,
        provider_continuously_available=True,
        actual_denial_observed=False,
        unchanged_work_scope_authority=True,
        authorized_ready_and_noncapacity_gates_pass=False,
    )
    assert evaluate_capacity_liveness(evidence).route == "NO_CAPACITY_LIVENESS_ACTION"


def test_policy22_liveness_weekly_or_sub5h_never_triggers():
    from automation.engine.execution_capacity import (
        CapacityLivenessEvidence,
        evaluate_capacity_liveness,
    )

    base = CapacityLivenessEvidence(
        only_blocker="WAIT_5H_CAPACITY",
        blocked_minutes=300,
        window_type="PRIMARY_5H",
        primary_window_minutes=300,
        reset_boundary_crossed=True,
        provider_continuously_available=True,
        actual_denial_observed=False,
        unchanged_work_scope_authority=True,
        authorized_ready_and_noncapacity_gates_pass=True,
    )

    weekly = replace(base, window_type="SECONDARY_WEEKLY")
    assert evaluate_capacity_liveness(weekly).route == "NO_CAPACITY_LIVENESS_ACTION"

    sub5h = replace(base, primary_window_minutes=299, blocked_minutes=299)
    assert evaluate_capacity_liveness(sub5h).route == "NO_CAPACITY_LIVENESS_ACTION"
