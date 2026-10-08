"""真實 candidate packages/非執行 handoff 的結構與邊界驗證。"""

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", ["P01", "P02"])
def test_real_candidate_scope_matches_context_registration(name):
    package = read(f"docs/program/packages/{name}.candidate.v1.json")
    Draft202012Validator(read("automation/platform/package.schema.v1.json")).validate(package)
    policy = read("automation/platform/context_policy.v1.json")
    assert package["identity"]["baseline_sha"] == policy["source_baseline_sha"]
    assert set(package["authority"]["exact_scope"]) == set(policy["packages"][name]["allowed_exact"])
    assert policy["packages"][name]["allowed_prefixes"] == []
    assert package["authority"]["parent_wave_grant"] is None
    assert package["dependencies"]["required_packages"] == ["P00"]
    assert package["design"]["public_semantic_gaps"]  # Not silently passed to an executor.


def test_handoff_cannot_be_relabelled_as_execution_grant():
    schema = read("automation/platform/handoff.schema.v1.json")
    value = {"schema_version": "p00.handoff.v1", "purpose": "PLANNING_ONLY", "producer_role": "WORK",
        "consumer_role": "REVIEWER", "package_id": "P01", "source_baseline_sha": "a" * 40,
        "planning_snapshot_sha": "b" * 40, "context_hash": "0" * 64, "package_hash": "1" * 64,
        "scope_hash": "2" * 64, "compiler_source_blob": "c" * 40,
        "artifact_refs": [{"path": "result.json", "sha256": "3" * 64}], "unresolved_findings": ["P00 not accepted"],
        "required_next_action": "Finish missing semantics", "authority": "NONE_PLANNING_OR_REVIEW_ONLY",
        "execution_eligible": False}
    validator = Draft202012Validator(schema)
    validator.validate(value)
    value["consumer_role"] = "CODEX"
    value["execution_eligible"] = True
    with pytest.raises(ValidationError):
        validator.validate(value)
