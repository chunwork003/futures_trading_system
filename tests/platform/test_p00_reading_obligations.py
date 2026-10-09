"""Source mapping不可刪除negative、安全scope、source conflict或UNKNOWN。"""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from scripts.p00_context import Snapshot, canonical
from scripts.p00_reading_obligations import verify, source_document

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = json.loads((ROOT / "automation/platform/source_reading_obligations.v1.json").read_text(encoding="utf-8"))


def test_pinned_source_sections_reconstruct_each_selected_unit():
    snapshot = Snapshot(ROOT, REGISTRY["source_candidate"])
    for path, document in REGISTRY["source_documents"].items():
        assert canonical(source_document(snapshot, path)) == canonical(document)
    assert verify(REGISTRY, REGISTRY)["execution_eligible"] is False


@pytest.mark.parametrize("mutation", ["negative", "protected", "source_hash", "schema", "endpoint", "intake", "budget", "acceptance", "conflict", "fallback", "latest_result"])
def test_omission_or_fake_success_is_rejected(mutation):
    candidate = deepcopy(REGISTRY)
    if mutation == "negative": candidate["critical_semantic_obligations"] = [o for o in candidate["critical_semantic_obligations"] if not o["id"].startswith("NEG-")]
    if mutation == "protected": candidate["critical_semantic_obligations"] = [o for o in candidate["critical_semantic_obligations"] if o["kind"] != "PROTECTED_SEMANTICS"]
    if mutation == "source_hash": next(iter(candidate["source_documents"].values()))["source"]["sha256"] = "0" * 64
    if mutation == "schema": candidate["packages"]["P01"]["schema_reading_obligations"].pop()
    if mutation == "endpoint": candidate["packages"]["P02"]["endpoint_reading_obligations"].pop()
    if mutation == "intake": candidate["intake"]["observation"]["observations"]["stop"]["knowledge"] = "NONE"
    if mutation == "budget": candidate["packages"]["P01"]["size_gate"] = "PASSED"
    if mutation == "acceptance": candidate["completion"]["acceptance"] = True
    if mutation == "conflict": candidate["source_findings"][1]["status"] = "RESOLVED"
    if mutation == "fallback": next(iter(candidate["source_documents"].values()))["full_source_fallback"] = False
    if mutation == "latest_result": candidate["result_dependencies"]["records"].pop()
    with pytest.raises(ValueError): verify(candidate, REGISTRY)


def test_full_sources_schema_closure_unknown_and_conflicts_remain_open():
    negatives = [o for o in REGISTRY["critical_semantic_obligations"] if o["id"].startswith("NEG-")]
    assert len(negatives) == 13
    assert all(o["packages"] == ["P01", "P02"] for o in negatives)
    assert REGISTRY["source_findings"][1]["level"] == 3
    assert REGISTRY["source_findings"][1]["status"] == "ARCHITECT_DECISION_REQUIRED_NO_SOURCE_REWRITE"
    for pid, package in REGISTRY["packages"].items():
        assert len(package["mandatory_sources"]) == len(package["mandatory_full_read_obligations"])
        assert package["original_mandatory_bytes"] > package["target_max_bytes"]
        assert package["selective_pack_bytes"] > package["target_max_bytes"]
        assert package["compiler_gate_changed"] is False
    assert REGISTRY["intake"]["observation"]["observations"]["stop"]["knowledge"] == "UNKNOWN"
    assert REGISTRY["reading_receipt"]["actual_reading_verified"] is False
