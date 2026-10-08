"""Requirement mapping 與非執行 scheduler proposal 的負例；不啟用controller。"""

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess

from jsonschema import Draft202012Validator, ValidationError
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_every_original_requirement_is_bound_and_not_claimed_implemented():
    mapping = read("automation/platform/automation_mapping.v1.json")
    assert [r["package_id"] for r in mapping["items"]] == [f"AUTO-IMP-{i:03}" for i in range(3, 10)]
    for item in mapping["items"]:
        raw = subprocess.check_output(["git", "--no-replace-objects", "-C", str(ROOT),
            "show", item["source_baseline"] + ":" + item["source_path"]])
        assert hashlib.sha256(raw).hexdigest() == item["source_sha256"]
        assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == item["source_git_blob"]
        source = yaml.safe_load(raw.decode("utf-8-sig"))
        assert [r["source_requirement"] for r in item["acceptance_mapping"]] == source["acceptance_tests"]
        assert [r["source_index"] for r in item["acceptance_mapping"]] == list(range(len(source["acceptance_tests"])))
        assert item["implementation_credit"] == "NOT_ASSERTED_BY_MAPPING"
    source = mapping["assertion_source"]
    raw = subprocess.check_output(["git", "--no-replace-objects", "-C", str(ROOT),
        "show", source["baseline_sha"] + ":" + source["path"]])
    assert hashlib.sha256(raw).hexdigest() == source["sha256"]
    assertions = yaml.safe_load(raw.decode("utf-8-sig"))
    expected = {key for group in ("authorization", "quota", "telemetry", "reentry") for key in assertions[group]}
    assert set(mapping["assertion_destinations"]) == expected
    assert mapping["accepted_policy_override"] is False
    assert mapping["execution_eligible"] is False


def proposal():
    return {"schema_version": "p00.scheduler_proposal.v1", "status": "CANDIDATE_NOT_AUTHORITY",
        "baseline_sha": "a" * 40, "policy_binding": "fixture-only", "action": "PROPOSE_PACKAGE",
        "priority_class": "NEW_WORK", "upstream_route": "READY_FOR_MANUAL_DISPATCH",
        "dispatch_mode": "MANUAL", "capacity_route": "ALLOW_WITH_WATCH",
        "gates": {k: True for k in ["exact_authority", "dependencies_ready", "lane_permits",
            "writer_available", "provider_available", "scope_ready", "external_clear", "forecast_known", "promotion_ready"]},
        "selected_package": "P01", "next_wake_utc": "2026-10-09T02:00:00Z", "wake_reason": "RECHECK",
        "schedule_generation": 1, "dedupe_subject": "P01", "relevant_revision": "5", "lifecycle_generation": 0,
        "evidence_refs": [{"path": "fixture.json", "sha256": "0" * 64}],
        "execution_eligible": False, "side_effects": "NONE",
        "limitations": "Proposal only; revalidate accepted route, authority and source before any effect."}


def validator():
    return Draft202012Validator(read("automation/platform/scheduler_proposal.schema.v1.json"))


@pytest.mark.parametrize("gate", ["exact_authority", "dependencies_ready", "lane_permits", "writer_available",
    "provider_available", "scope_ready", "external_clear", "forecast_known"])
def test_any_hard_gate_blocks_package_proposal(gate):
    value = proposal()
    value["gates"][gate] = False
    with pytest.raises(ValidationError):
        validator().validate(value)


@pytest.mark.parametrize("priority", ["SAFETY_GOVERNANCE", "UNFINISHED", "RESULT_REVIEW_INTEGRATION"])
def test_priority_work_cannot_be_overridden_by_new_package(priority):
    value = proposal()
    value["priority_class"] = priority
    with pytest.raises(ValidationError):
        validator().validate(value)
    value.update(action="REENTRY", selected_package=None)
    validator().validate(value)


def test_manual_watch_is_not_controlled_auto_capacity_or_promotion():
    value = proposal()
    value["gates"]["promotion_ready"] = False
    validator().validate(value)
    value["dispatch_mode"] = "CONTROLLED_AUTO"
    with pytest.raises(ValidationError):
        validator().validate(value)
    value.update(capacity_route="CONTROLLED_AUTO_CAPACITY_FIT", upstream_route="CONTROLLED_AUTO_DISPATCH_ELIGIBLE")
    with pytest.raises(ValidationError):
        validator().validate(value)
    value["gates"]["promotion_ready"] = True
    validator().validate(value)


def test_proposal_never_grants_execution_or_adds_external_effect():
    for field, replacement in [("execution_eligible", True), ("side_effects", "DISPATCH")]:
        value = proposal()
        value[field] = replacement
        with pytest.raises(ValidationError):
            validator().validate(value)


def test_fixed_rational_score_vectors():
    # 對照文件公式的精確數值，並非另一個可執行scheduler。
    benefit = Fraction(4 * 1000 + 3 * 1000, 1000)
    cost = Fraction(1000000, 1000000) + Fraction(28800, 28800)
    assert benefit / max(cost, Fraction(1, 10)) == Fraction(7, 2)
    assert Fraction(9000, 1000) / (cost + 2) == Fraction(9, 4)
    assert min(1000, int(Fraction(604800, 1) / Fraction(3024, 5))) == 1000
