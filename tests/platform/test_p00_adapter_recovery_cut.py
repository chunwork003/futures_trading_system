"""R01 DTO source coverage 與 composite-cut 反例；pure spec oracle，不接入 runtime。"""

import copy
import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, ValidationError
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from p00_adapter_contract import canonical, validate_mapping
from p00_context import Snapshot

CONTRACTS = ROOT / "docs/architecture/contracts"
MAP = json.loads((CONTRACTS / "dto_store_map.v1.json").read_text(encoding="utf-8"))
SPECS = [json.loads((ROOT / path).read_text(encoding="utf-8")) for path in MAP["schema_sources"]]
CUT_SCHEMA = json.loads((CONTRACTS / "decision_input_cut.schema.v1.json").read_text(encoding="utf-8"))
FIXTURE = json.loads((CONTRACTS / "decision_input_cut.fixture.v1.json").read_text(encoding="utf-8"))


def current_inputs(captured, current, trusted_manifest):
    """只比較 specification fixture；trusted manifest 的真實解析／DB fence 仍待 P08。"""
    validator = Draft202012Validator(CUT_SCHEMA)
    for cut in (captured, current):
        validator.validate(cut)
        for key in ("input_profile", "account", "session_id", "cohort_id", "instrument_id", "contract_id"):
            if cut[key] != trusted_manifest[key]:
                raise ValueError("SCOPE_MISMATCH")
        if cut["dependency_manifest_hash"] != hashlib.sha256(canonical(trusted_manifest)).hexdigest():
            raise ValueError("MANIFEST_MISMATCH")
        keys = [(item["kind"], item["key"]) for item in cut["dependencies"]]
        required = [(item["kind"], item["key"]) for item in trusted_manifest["required_dependencies"]]
        if not required or required != sorted(set(required)) or keys != required:
            raise ValueError("DEPENDENCY_CLOSURE_MISMATCH")
    if captured != current:
        raise ValueError("STALE_INPUT_CUT")
    return "CURRENT_INPUTS_ONLY_NOT_PERMISSION"


def cuts():
    return copy.deepcopy(FIXTURE["captured_cut"]), copy.deepcopy(FIXTURE["captured_cut"])


def test_all_shared_dtos_have_source_bound_store_or_explicit_nonstore_mapping():
    result = validate_mapping(MAP, SPECS, Snapshot(ROOT, MAP["source_master"]))
    assert result["status"] == "CANDIDATE_STRUCTURE_PASS"
    assert result["schemas"] == 70
    assert result["execution_eligible"] is False
    assert result["adapter_conformance"] == "NOT_IMPLEMENTED"


@pytest.mark.parametrize("mutation,reason", [
    ("missing", "DTO_COVERAGE"), ("duplicate", "DTO_COVERAGE"), ("new_schema", "DTO_COVERAGE"),
    ("changed_schema", "SCHEMA_MATERIAL"), ("owner_missing", "OWNER_MISSING"),
    ("blob_changed", "BLOB_MISMATCH"), ("qualified", "QUALIFICATION"), ("accepted", "CANNOT_ASSERT"),
    ("field_missing", "FIELD_SOURCE_INCOMPLETE")])
def test_mapping_cannot_hide_missing_coverage_material_drift_or_fake_qualification(mutation, reason):
    mapping, specs = copy.deepcopy(MAP), copy.deepcopy(SPECS)
    if mutation == "missing":
        mapping["mappings"].pop()
    elif mutation == "duplicate":
        mapping["mappings"].append(mapping["mappings"][0])
    elif mutation == "new_schema":
        for spec in specs:
            spec["components"]["schemas"]["UnownedNewDto"] = {"type": "string"}
    elif mutation == "changed_schema":
        for spec in specs:
            spec["components"]["schemas"]["Signal"]["properties"]["strategy_instance_id"] = {"type": "integer"}
    elif mutation == "owner_missing":
        mapping["mappings"][0]["mapping_group"] = "unowned"
    elif mutation == "blob_changed":
        mapping["source_bindings"][0]["sha256"] = "0" * 64
    elif mutation == "qualified":
        mapping["groups"]["signal"]["adapter_state"] = "QUALIFIED"
    elif mutation == "field_missing":
        del mapping["new_record_field_sources"]["Signal"]["state_snapshot_ref"]
    else:
        mapping["status"] = "ACCEPTED"
    with pytest.raises(ValueError, match=reason):
        validate_mapping(mapping, specs, Snapshot(ROOT, mapping["source_master"]))


def test_unchanged_complete_cut_is_only_current_inputs_not_readiness_permission():
    Draft202012Validator.check_schema(CUT_SCHEMA)
    captured, current = cuts()
    assert current_inputs(captured, current, FIXTURE["trusted_manifest"]) == FIXTURE["expected_unchanged_result"]


@pytest.mark.parametrize("kind", ["COHORT_POLICY", "STRATEGY_CONTEXT", "STRATEGY_OUTPUT", "COMPLETENESS",
                                   "OBSERVATION", "CAPITAL", "MARK", "MARGIN", "RISK_POLICY", "SESSION_CONTROL"])
def test_each_material_change_invalidates_even_without_account_or_selector_revision_advance(kind):
    captured, current = cuts()
    item = next(row for row in current["dependencies"] if row["kind"] == kind)
    item["payload_hash"] = "d" * 64
    assert current["base_account_cut"] == captured["base_account_cut"]
    assert current["selection_revision"] == captured["selection_revision"]
    with pytest.raises(ValueError, match="STALE_INPUT_CUT"):
        current_inputs(captured, current, FIXTURE["trusted_manifest"])


@pytest.mark.parametrize("mutation", ["missing", "extra", "duplicate", "reorder"])
def test_schema_valid_shape_cannot_shrink_or_expand_authoritative_dependency_closure(mutation):
    captured, current = cuts()
    if mutation == "missing":
        current["dependencies"].pop()
    elif mutation == "extra":
        extra = copy.deepcopy(current["dependencies"][0])
        extra["key"] = "unrequired-strategy"
        current["dependencies"].append(extra)
    elif mutation == "duplicate":
        current["dependencies"].append(current["dependencies"][0])
    else:
        current["dependencies"].reverse()
    Draft202012Validator(CUT_SCHEMA).validate(current)
    with pytest.raises(ValueError, match="DEPENDENCY_CLOSURE"):
        current_inputs(captured, current, FIXTURE["trusted_manifest"])


@pytest.mark.parametrize("key,new", [("account", {"broker": "SIMULATED", "account_ref": "account-2"}),
                                     ("session_id", "session-2"), ("cohort_id", "cohort-2"),
                                     ("contract_id", 2), ("instrument_id", 2)])
def test_even_two_equal_cuts_cannot_override_trusted_account_session_or_membership_scope(key, new):
    captured, current = cuts()
    captured[key] = current[key] = new
    with pytest.raises(ValueError, match="SCOPE_MISMATCH"):
        current_inputs(captured, current, FIXTURE["trusted_manifest"])


def test_untrusted_shrunken_manifest_cannot_validate_by_rehashing_both_cuts():
    captured, current = cuts()
    untrusted = copy.deepcopy(FIXTURE["trusted_manifest"])
    untrusted["required_dependencies"].pop()
    for cut in (captured, current):
        cut["dependencies"].pop()
        cut["dependency_manifest_hash"] = hashlib.sha256(canonical(untrusted)).hexdigest()
    with pytest.raises(ValueError, match="MANIFEST_MISMATCH"):
        current_inputs(captured, current, FIXTURE["trusted_manifest"])


@pytest.mark.parametrize("mutation", ["aba", "head_advance", "recovery_state", "bundle_change"])
def test_aba_current_selection_and_account_recovery_transition_invalidate(mutation):
    captured, current = cuts()
    if mutation == "aba":
        current["dependencies"][0]["selector_revision"] += 2
    elif mutation == "head_advance":
        current["selection_revision"] += 1
    elif mutation == "recovery_state":
        current["base_account_cut"]["recovery_state"] = "ACTIVE"
    else:
        current["base_account_cut"]["trusted_bundle_fingerprint"] = "d" * 64
    assert captured["base_account_cut"]["account_revision"] == current["base_account_cut"]["account_revision"]
    with pytest.raises(ValueError, match="STALE_INPUT_CUT"):
        current_inputs(captured, current, FIXTURE["trusted_manifest"])


@pytest.mark.parametrize("mutation", ["missing_head", "unknown", "fake_ready"])
def test_absence_unknown_and_caller_ready_cannot_pass_schema(mutation):
    captured, current = cuts()
    if mutation == "missing_head":
        del current["selection_revision"]
    elif mutation == "unknown":
        current["dependencies"][0]["record_id"] = None
    else:
        current["ready"] = True
    with pytest.raises(ValidationError):
        current_inputs(captured, current, FIXTURE["trusted_manifest"])


def final_inputs(captured, current):
    """Synthetic final witness comparison；GRANTED 仍需外部 trusted resolver/auth/risk validation。"""
    schema = {"$ref": "#/$defs/FinalSubmissionWitness", "$defs": CUT_SCHEMA["$defs"]}
    for witness in (captured, current):
        Draft202012Validator(schema).validate(witness)
        selection = witness["permission_selection"]
        if (selection["decision_id"] != witness["decision_ref"]["id"]
                or selection["risk_decision_id"] != witness["risk_ref"]["id"]):
            raise ValueError("PERMISSION_REFERENCE_MISMATCH")
        if selection["disposition"] != "GRANTED":
            raise ValueError("PERMISSION_REVOKED")
    current_inputs(captured["input_cut"], current["input_cut"], FIXTURE["trusted_manifest"])
    if captured != current:
        raise ValueError("STALE_FINAL_WITNESS")
    return "CURRENT_FINAL_REFERENCES_ONLY_NOT_AUTHORIZATION"


def test_final_witness_is_typed_but_not_a_trading_authorization():
    witness = FIXTURE["final_submission_witness"]
    assert final_inputs(witness, witness) == "CURRENT_FINAL_REFERENCES_ONLY_NOT_AUTHORIZATION"


@pytest.mark.parametrize("mutation", ["revoke", "aba", "decision", "risk", "trigger"])
def test_unchanged_risk_payload_cannot_hide_revocation_or_reference_selection_change(mutation):
    captured = copy.deepcopy(FIXTURE["final_submission_witness"])
    current = copy.deepcopy(captured)
    if mutation == "revoke":
        current["permission_selection"]["disposition"] = "REVOKED"
    elif mutation == "aba":
        current["permission_selection"]["selector_revision"] += 2
    else:
        current[mutation + "_ref"]["id"] = mutation + "-2"
    assert captured["risk_ref"]["payload_hash"] == current["risk_ref"]["payload_hash"]
    with pytest.raises(ValueError, match="PERMISSION_REVOKED|PERMISSION_REFERENCE_MISMATCH|STALE_FINAL_WITNESS"):
        final_inputs(captured, current)
