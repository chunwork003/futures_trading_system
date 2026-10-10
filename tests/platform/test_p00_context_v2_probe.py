"""Context V2 的安全反例；不把 exact projection 當閱讀／語意／runtime qualification。"""
from copy import deepcopy
import json
from pathlib import Path
import pytest
import yaml
from scripts.p00_context import canonical
from scripts.p00_context_pack import expand_json
from scripts.p00_context_v2_probe import build_graph, capsule, omission_oracle, sha

ROOT = Path(__file__).resolve().parents[2]
BASELINE = "6b717d5b7b9447272e5ff35b7715ad33ad6fb026"
PROFILE = "CONTRACT_REVIEW_NO_EFFECTS"

@pytest.fixture(scope="module")
def bound_capsule():
    graph = build_graph(ROOT, BASELINE, "P02")
    return capsule(graph, "P02.IMPORT", ROOT, PROFILE)

def test_complete_negative_source_and_references_survive_read_only_stage(bound_capsule):
    docs = bound_capsule["documents"]
    negative = next(n for n in docs if n["id"].endswith("negative_assertions.v2.yaml"))
    value = yaml.safe_load(negative["value"])
    assert len(value["semantics"]["denied"]) == 13
    assert len(value["invariants"]) == 7
    assert len(bound_capsule["negative_ids"]) == 20
    assert bound_capsule["deferred_preflight_sources"]
    for owner in ["python", "bff"]:
        n = next(n for n in docs if n["id"] == "API:" + owner)
        projected = expand_json(n["value"], bound_capsule["schema_pool"])
        original = json.loads((ROOT / n["source"]["path"]).read_text(encoding="utf-8"))
        assert projected["security"] == original["security"]
        assert projected["components"]["securitySchemes"] == original["components"]["securitySchemes"]
        for p in n["selector"]["paths"]:
            assert projected["paths"][p] == original["paths"][p]
        for name, schema in projected["components"]["schemas"].items():
            assert schema == original["components"]["schemas"][name]
    assert bound_capsule["execution_eligible"] is False
    assert bound_capsule["authority"] == "NONE"

@pytest.mark.parametrize("defect", ["negative", "security", "error", "reference", "stale", "scope", "authority"])
def test_source_derived_oracle_rejects_rehashed_adverse_capsule(bound_capsule, defect):
    supplied = deepcopy(bound_capsule)
    if defect == "negative":
        n = next(n for n in supplied["documents"] if n["id"].endswith("negative_assertions.v2.yaml"))
        n["value"] = n["value"].replace("  - CONSUMED_REDISPATCH\n", "")
    elif defect in {"security", "error", "reference"}:
        n = next(n for n in supplied["documents"] if n["id"] == "API:bff")
        if defect == "security":
            n["value"]["value"]["security"] = []
        elif defect == "error":
            operation = n["value"]["value"]["paths"]["/api/v1/dataset-imports"]["post"]
            operation["responses"].pop("401")
        else:
            supplied["schema_pool"].pop(next(iter(supplied["schema_pool"])))
    elif defect == "stale":
        supplied["baseline"] = "0" * 40
    elif defect == "scope":
        supplied["changed_paths"].append("trading/execution.py")
    else:
        supplied["authority"] = "ACCEPTED"
        supplied["execution_eligible"] = True
    for n in supplied["documents"]:
        n["value_sha256"] = sha(canonical(n["value"]))
    with pytest.raises(ValueError, match="OMISSION_STALE_SCOPE_OR_SOURCE_DRIFT"):
        omission_oracle(ROOT, BASELINE, "P02", "P02.IMPORT", supplied, profile=PROFILE)

def test_stop_wins_even_for_exact_previous_capsule(bound_capsule):
    with pytest.raises(ValueError, match="STOP_REQUIRES_REENTRY"):
        omission_oracle(ROOT, BASELINE, "P02", "P02.IMPORT", bound_capsule, stop=True, profile=PROFILE)

def test_cross_owner_scope_requires_an_explicit_stage():
    with pytest.raises(ValueError, match="CROSS_PACKAGE"):
        capsule({"package": "P01"}, "P02.IMPORT", ROOT, PROFILE)
    with pytest.raises(ValueError, match="UNKNOWN_STAGE_PROFILE"):
        capsule({"package": "P01"}, "P01.CSV", ROOT, "READY_FOR_EXECUTION")

def test_exact_projection_is_still_not_a_reading_qualification(bound_capsule):
    result = omission_oracle(ROOT, BASELINE, "P02", "P02.IMPORT", bound_capsule, profile=PROFILE)
    assert result == "EXACT_PROJECTION_ONLY_SEMANTIC_REVIEW_AND_INJECTION_NOT_ASSERTED"
