"""工程制度的來源／未知量測／golden隔離反例；不冒充九類真實任務執行。"""

import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from p00_context import Snapshot
from p00_engineering import (forecast_error_preview, observation_preview, read_pointer,
                             validate_evaluation, validate_observation, verify_config)


def load(name):
    return json.loads((ROOT / "automation/platform" / name).read_text(encoding="utf-8"))


CONFIG = load("engineering_system.v1.json")
FIXTURE = load("engineering_system.fixture.v1.json")
OBS_SCHEMA = load("engineering_observation.schema.v1.json")
EVAL_SCHEMA = load("golden_evaluation.schema.v1.json")
CANDIDATE = Snapshot(ROOT, CONFIG["source_candidate"])
MASTER = Snapshot(ROOT, CONFIG["source_master"])
SNAPSHOTS = {s.baseline: s for s in (CANDIDATE, MASTER)}


def test_actual_git_sources_and_owner_obligations_are_bound_without_qualification():
    result = verify_config(CONFIG, CANDIDATE, MASTER)
    assert (result["delivery_clauses"], result["golden_families"], result["kpis"]) == (10, 9, 14)
    assert result["actual_golden_runs"] == result["new_v1_credit"] == 0
    assert result["execution_eligible"] is False and result["qualification"] == "NOT_QUALIFIED"
    assert result["source_refs"] == len(CONFIG["source_evidence"])


@pytest.mark.parametrize("mutation,reason", [
    (lambda x: x.update(authority="ACCEPTED"), "NOT_ACCEPTANCE"),
    (lambda x: x.update(new_v1_credit=False), "NOT_ACCEPTANCE"),
    (lambda x: x.update(independent_review="PASS"), "NOT_ACCEPTANCE"),
    (lambda x: x.update(controller_enabled=True), "FIELDS_INVALID"),
    (lambda x: x["source_evidence"][0].update(sha256="0" * 64), "BLOB_MISMATCH"),
    (lambda x: x["source_evidence"].append(copy.deepcopy(x["source_evidence"][0])), "DUPLICATE"),
    (lambda x: x.update(source_evidence=[r for r in x["source_evidence"]
                                       if r["path"] != "docs/program/current_truth.v1.json"]), "SOURCE_MISSING"),
    (lambda x: x["owner_delivery_clause_ids"].pop(), "CLAUSES_MISSING"),
    (lambda x: x["templates"][0].update(id="T-unknown"), "KIND_SET"),
    (lambda x: x["templates"][0].update(default_disposition="ACCEPTED"), "PREFILL_ACCEPTANCE"),
    (lambda x: x["generators"].pop(), "KIND_SET"),
    (lambda x: x["generators"][0].update(generated_semantics="INFER_AUTHORITY"), "CREATE_SEMANTICS"),
    (lambda x: x["golden_tasks"][0].update(actual_evaluation_status="PASS"), "ACTUALLY_QUALIFIED"),
    (lambda x: x["kpis"][0].update(current_qualified_value=0), "QUALIFICATION_NOT_ESTABLISHED"),
    (lambda x: x["telemetry"].update(unknown_is_not_zero=False), "TRUST_NOT_ESTABLISHED"),
    (lambda x: x["telemetry"]["skill_metrics"].pop(), "METRICS_INCOMPLETE"),
    (lambda x: x["optimization"]["states"].remove("INDEPENDENT_REVIEW"), "STAGE_CANNOT_BE_SKIPPED"),
    (lambda x: x["optimization"].update(current_roi="1"), "GAIN_OR_ACTIVATION"),
    (lambda x: x["roadmap"][4].update(current_status="QUALIFIED"), "QUALIFICATION_NOT_ESTABLISHED"),
    (lambda x: x["roadmap"][0].update(product_must_wait_for_all_phases=True), "STALL_PRODUCT"),
])
def test_forged_authority_missing_source_and_self_qualification_are_rejected(mutation, reason):
    config = copy.deepcopy(CONFIG)
    mutation(config)
    with pytest.raises(ValueError, match=reason):
        verify_config(config, CANDIDATE, MASTER)


def test_exact_source_scalar_and_replay_count_preserve_unknown_population_and_cost():
    event = FIXTURE["observation"]
    assert validate_observation(event, OBS_SCHEMA, SNAPSHOTS)["task_token_actual"] == "NOT_AVAILABLE"
    result = observation_preview([event, copy.deepcopy(event)], OBS_SCHEMA, SNAPSHOTS)
    assert result["canonical_spec_record_count"] == 1
    assert result["accepted_weight"] is None and result["population_completeness"] == "UNKNOWN"
    assert observation_preview([], OBS_SCHEMA, SNAPSHOTS)["population_completeness"] == "UNKNOWN"
    changed = copy.deepcopy(event)
    changed["recorded_at"] = "2026-10-09T01:00:01Z"
    with pytest.raises(ValueError, match="EVENT_ID_PAYLOAD_CONFLICT"):
        observation_preview([event, changed], OBS_SCHEMA, SNAPSHOTS)


@pytest.mark.parametrize("mutation,reason", [
    (lambda x: x.update(producer_qualification="QUALIFIED"), "SCHEMA_INVALID"),
    (lambda x: x.update(acceptance_receipt="PASS"), "SCHEMA_INVALID"),
    (lambda x: x["measurements"][0].update(value="0"), "SCHEMA_INVALID"),
    (lambda x: x["measurements"][0].update(status="OBSERVED", value="0",
        source_ref=copy.deepcopy(FIXTURE["observation"]["measurements"][1]["source_ref"]),
        source_pointer="/latest_p00_reentry/provider_observation_during_run/five_hour_used_percent"), "TRUSTED_INTAKE"),
    (lambda x: x["measurements"][1].update(value="34"), "VALUE_MISMATCH"),
    (lambda x: x["measurements"][1].update(value="101"), "OUT_OF_RANGE"),
    (lambda x: x["measurements"][1].update(scope="ACTOR_ATTEMPT"), "SCHEMA_INVALID"),
    (lambda x: x["measurements"][1].update(unit="TOKENS"), "SCHEMA_INVALID"),
    (lambda x: x["measurements"][1].update(value="NaN"), "SCHEMA_INVALID"),
    (lambda x: x["measurements"][1].update(value="1" * 41), "SCHEMA_INVALID"),
    (lambda x: x["measurements"][1]["source_ref"].update(sha256="0" * 64), "BLOB_MISMATCH"),
    (lambda x: x["measurements"][1].update(source_pointer="/missing"), "POINTER_NOT_FOUND"),
    (lambda x: x["measurements"][1].update(source_pointer="/bad~2escape"), "POINTER_ESCAPE_INVALID"),
    (lambda x: x["measurements"].append(copy.deepcopy(x["measurements"][1])), "NAME_DUPLICATE"),
])
def test_telemetry_cannot_convert_unknown_shared_quota_or_forged_receipts_to_actual_cost(mutation, reason):
    event = copy.deepcopy(FIXTURE["observation"])
    mutation(event)
    with pytest.raises(ValueError, match=reason):
        validate_observation(event, OBS_SCHEMA, SNAPSHOTS)


def test_estimated_fractional_count_is_rejected_and_forecast_cannot_be_observed():
    event = copy.deepcopy(FIXTURE["observation"])
    row = event["measurements"][0]
    row.update(name="EXPECTED_ACTOR_TOKENS", status="ESTIMATED", value="1.5")
    with pytest.raises(ValueError, match="NOT_FRACTIONAL"):
        validate_observation(event, OBS_SCHEMA, SNAPSHOTS)
    row["value"] = "1"
    validate_observation(event, OBS_SCHEMA, SNAPSHOTS)
    row.update(status="OBSERVED", source_ref=copy.deepcopy(event["measurements"][1]["source_ref"]),
               source_pointer=event["measurements"][1]["source_pointer"])
    with pytest.raises(ValueError, match="FORECAST_IS_ESTIMATE"):
        validate_observation(event, OBS_SCHEMA, SNAPSHOTS)


@pytest.mark.parametrize("trial", FIXTURE["evaluation_shapes"], ids=lambda t: t["task_family_id"])
def test_nine_shape_examples_remain_unrun_and_unqualified(trial):
    result = validate_evaluation(trial, EVAL_SCHEMA, CONFIG, SNAPSHOTS)
    assert result["effectiveness"] == "UNKNOWN" and result["qualification"] == "NOT_QUALIFIED"
    assert all(r["declared_outcome"] == "NOT_RUN" for side in ("baseline", "candidate") for r in trial[side]["cases"])


@pytest.mark.parametrize("mutation,reason", [
    (lambda x: x.update(qualification="QUALIFIED"), "SCHEMA_INVALID"),
    (lambda x: x.update(independent_review="PASS"), "SCHEMA_INVALID"),
    (lambda x: x.update(input_snapshot=MASTER.baseline), "SNAPSHOT_DRIFT"),
    (lambda x: x["candidate"].update(subject_sha="0" * 40), "SNAPSHOT_NOT_DECLARED"),
    (lambda x: x.update(task_family_id="G02"), "REFERENCE_MISMATCH"),
    (lambda x: x["candidate"].update(oracle_sha256="0" * 64), "ORACLE_OR_FIXTURE_DRIFT"),
    (lambda x: x["candidate"].update(environment_id="OTHER"), "UNMATCHED_GOLDEN_COHORT"),
    (lambda x: x["candidate"].update(contract_revision=2), "UNMATCHED_GOLDEN_COHORT"),
    (lambda x: x["candidate"]["cases"].pop(), "CASE_SET_INCOMPLETE"),
    (lambda x: x["candidate"]["cases"][1].update(case_id=x["candidate"]["cases"][0]["case_id"]), "CASE_SET_INCOMPLETE"),
    (lambda x: x["candidate"]["cases"][0].update(declared_outcome="DECLARED_PASS"), "ARTIFACT_REQUIRED"),
    (lambda x: x["candidate"]["cases"][0].update(artifact_sha256="0" * 64), "ARTIFACT_REQUIRED"),
])
def test_missing_negative_oracles_drift_and_fake_review_are_rejected(mutation, reason):
    trial = copy.deepcopy(FIXTURE["evaluation_shapes"][0])
    mutation(trial)
    with pytest.raises(ValueError, match=reason):
        validate_evaluation(trial, EVAL_SCHEMA, CONFIG, SNAPSHOTS)


def test_declared_pass_with_hash_still_cannot_qualify_or_claim_effectiveness():
    trial = copy.deepcopy(FIXTURE["evaluation_shapes"][0])
    for side in ("baseline", "candidate"):
        for case in trial[side]["cases"]:
            case.update(declared_outcome="DECLARED_PASS", artifact_sha256="0" * 64)
    result = validate_evaluation(trial, EVAL_SCHEMA, CONFIG, SNAPSHOTS)
    assert result["qualification"] == "NOT_QUALIFIED" and result["effectiveness"] == "UNKNOWN"


@pytest.mark.parametrize("forecast,actual,matched,reason", [
    (None, "1", True, "MISSING_OR_UNMATCHED_INPUTS"),
    ("0", None, True, "MISSING_OR_UNMATCHED_INPUTS"),
    ("1", "1", False, "MISSING_OR_UNMATCHED_INPUTS"),
    ("1", "1", 1, "MISSING_OR_UNMATCHED_INPUTS"),
    ("2", "0", True, "ZERO_ACTUAL_RELATIVE_UNDEFINED"),
])
def test_forecast_missing_scope_and_zero_denominator_do_not_fake_accuracy(forecast, actual, matched, reason):
    result = forecast_error_preview(forecast, actual, matched)
    assert result["reason"] == reason and result["relative_error"] is None and result["qualified"] is False


def test_decimal_arithmetic_stays_exact_without_qualifying_real_measurements():
    result = forecast_error_preview("0.1", "0.3", True)
    assert result["absolute_error"] == "0.2" and result["qualified"] is False
    assert forecast_error_preview("9999999999999999999999999999999999999999",
                                  "9999999999999999999999999999999999999998", True)["absolute_error"] == "1"


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-1", "1e4", "01", "1" * 41, True, 1])
def test_nondecimal_or_unbounded_forecast_inputs_are_rejected(value):
    with pytest.raises(ValueError, match="DECIMAL_INPUT_INVALID"):
        forecast_error_preview(value, "1", True)


def test_pointer_array_index_and_escaped_property_names_are_exact():
    assert read_pointer({"a/b": [{"x~y": "1"}]}, "/a~1b/0/x~0y") == "1"
    with pytest.raises(ValueError, match="POINTER_NOT_FOUND"):
        read_pointer([1], "/01")
