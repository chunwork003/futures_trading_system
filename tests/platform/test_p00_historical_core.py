"""Historical accepted weight 與新 V1 credit 隔離的來源／反例測試。"""

import copy
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from p00_context import Snapshot
from p00_historical_core import reconcile

REGISTRY = json.loads((ROOT / "docs/program/accepted_core_reconciliation.v1.json").read_text(encoding="utf-8"))
LEDGER = json.loads((ROOT / "docs/program/program_baseline.v1.json").read_text(encoding="utf-8"))


def test_26_core_leaves_are_113_historical_weight_not_new_product_credit():
    result = reconcile(REGISTRY, LEDGER, Snapshot(ROOT, REGISTRY["source_master"]))
    assert result["leaf_count"] == 26
    assert result["accepted_scope_weight"] == 113
    assert result["new_v1_credit"] == 0
    assert result["product_completion"] == "UNCALIBRATED"
    assert result["execution_eligible"] is False


@pytest.mark.parametrize("mutation,reason", [
    ("weight", "WEIGHT_CHANGED"), ("missing", "COUNT_OR_ID"), ("duplicate", "COUNT_OR_ID"),
    ("credit", "NOT_NEW_V1_CREDIT"), ("count", "NOT_LEAF_COUNT"),
    ("blob", "BLOB_MISMATCH"), ("wrong_row", "ROW_SOURCE_MISMATCH"),
    ("unknown_link", "UNKNOWN_DELTA_LINK"), ("claim_complete", "CALIBRATION"),
    ("original_accepted", "EXCLUSIONS"), ("runtime", "RUNTIME_MISMATCH")])
def test_reconciliation_rejects_fabricated_evidence_count_credit_and_scope(mutation, reason):
    registry = copy.deepcopy(REGISTRY)
    if mutation == "weight":
        registry["core"][0]["accepted_scope_weight"] += 1
    elif mutation == "missing":
        registry["core"].pop()
    elif mutation == "duplicate":
        registry["core"].append(copy.deepcopy(registry["core"][0]))
    elif mutation == "credit":
        registry["core"][0]["new_v1_credit"] = registry["core"][0]["accepted_scope_weight"]
    elif mutation == "count":
        registry["totals"]["leaf_count"] = 113
    elif mutation == "blob":
        registry["source_evidence"][0]["sha256"] = "0" * 64
    elif mutation == "wrong_row":
        registry["core"][0]["source_row"]["line"] += 1
    elif mutation == "unknown_link":
        registry["core"][0]["v1_delta_deliverables"] = ["UNKNOWN"]
    elif mutation == "claim_complete":
        registry["full_historical_requirement_coverage"] = "COMPLETE"
    elif mutation == "original_accepted":
        registry["excluded"]["original_35_151_candidate"] = "ACCEPTED"
    else:
        registry["accepted_runtime_head"] = registry["source_master"]
    with pytest.raises(ValueError, match=reason):
        reconcile(registry, LEDGER, Snapshot(ROOT, registry["source_master"]))
