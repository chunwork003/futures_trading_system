"""Compiler negative fixtures：candidate compilation 不等於 legal execution。"""

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError

from scripts.p00_compile import compile_candidate
from scripts.p00_context import canonical

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "automation/platform/package.schema.v1.json").read_text(encoding="utf-8"))


def inputs():
    package = {"schema_version": "p00.package.v1", "identity": {"package_id": "P00", "revision": 1,
        "baseline_sha": "a" * 40, "requirement_ids": ["REQ-62"], "deliverable_weights": {"D1": 1}},
        "authority": {"parent_wave_grant": None, "exact_scope": ["docs/architecture/example.md"],
            "protected_scope": ["trading/execution.py"], "allowed_side_effects": ["SCOPE_WRITE"], "correction_budget": 2},
        "design": {"status": "DEFINED_CANDIDATE", "owners": ["ARCHITECT"], "input_output_schemas": ["fixture-schema"],
            "state_transitions": ["candidate -> review pending"], "transaction_boundary": "single candidate commit",
            "idempotency_and_recovery": "same revision hash replay", "error_and_unknown_semantics": "reject missing evidence",
            "compatibility_rules": ["do not modify accepted source"], "public_semantic_gaps": []},
        "dependencies": {"required_acceptances": [], "external_gates": [], "parallel_or_parked_work": []},
        "verification": {k: ["explicit fixture reference"] for k in ("positive_examples", "counterexamples", "targeted_tests",
            "integration_tests", "regression_impact_set", "independent_review_scope")},
        "completion": {"evidence_artifacts": ["result.json"], "acceptance_checks": ["independent review bound to candidate"],
            "stop_conditions": ["unresolved public semantics"]}}
    context = {"schema_version": "p00.context_manifest.v1", "request": {"baseline_sha": "a" * 40,
        "package_id": "P00", "changed_paths": ["docs/architecture/example.md"]}, "authority": "NONE_CONTEXT_ONLY",
        "execution_eligible": False, "evidence_refs": [], "context_budget": {"status": "WITHIN_TARGET"}}
    return package, seal(context)


def seal(context):
    context = {k: v for k, v in context.items() if k != "context_hash"}
    return {**context, "context_hash": hashlib.sha256(canonical(context)).hexdigest()}


def test_compilation_is_deterministic_and_never_grants_authority():
    package, context = inputs()
    first = compile_candidate(package, context, SCHEMA)
    assert first == compile_candidate(deepcopy(package), deepcopy(context), SCHEMA)
    assert first["status"] == "COMPILED_CANDIDATE_PENDING_INDEPENDENT_REVIEW"
    assert first["authority"] == "NONE_COMPILATION_ONLY" and first["execution_eligible"] is False
    assert "CURRENT_EXACT_AUTHORIZATION" in first["unevaluated_gates"]


def test_context_tampering_is_rejected():
    package, context = inputs()
    context["request"]["changed_paths"].append("trading/execution.py")
    with pytest.raises(ValueError, match="CONTEXT_HASH_MISMATCH"):
        compile_candidate(package, context, SCHEMA)


@pytest.mark.parametrize("mutation,reason", [("baseline", "BASELINE_MISMATCH"), ("scope", "CONTEXT_SCOPE_MISMATCH"),
    ("protected", "PROTECTED_SCOPE_OVERLAP"), ("dependency", "DEPENDENCY_EVIDENCE_NOT_BOUND")])
def test_boundaries_reject_inconsistent_package(mutation, reason):
    package, context = inputs()
    if mutation == "baseline": package["identity"]["baseline_sha"] = "b" * 40
    if mutation == "scope": package["authority"]["exact_scope"] = ["docs/architecture/another.md"]
    if mutation == "protected": package["authority"]["protected_scope"] = package["authority"]["exact_scope"]
    if mutation == "dependency": package["dependencies"]["required_acceptances"] = [{"path": "missing.json", "sha256": "0" * 64}]
    with pytest.raises(ValueError, match=reason):
        compile_candidate(package, context, SCHEMA)


def test_design_gaps_and_large_context_stay_not_ready():
    package, context = inputs()
    package["design"]["public_semantic_gaps"] = ["Unspecified recovery frontier"]
    context["context_budget"]["status"] = "OVER_TARGET_REQUIRES_COMPACTION"
    result = compile_candidate(package, seal(context), SCHEMA)
    assert result["status"] == "PACKAGE_NOT_READY"
    assert set(result["not_ready_reasons"]) == {"PUBLIC_SEMANTIC_GAPS", "CONTEXT_COMPACTION_REQUIRED"}


def test_missing_recovery_contract_cannot_compile():
    package, context = inputs()
    del package["design"]["idempotency_and_recovery"]
    with pytest.raises(ValidationError):
        compile_candidate(package, context, SCHEMA)
