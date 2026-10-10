"""修正審查驗證原始條款、exact patch 及不可自動提升的資格；不測產品 parser。"""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from scripts.p00_review_fix import DECISION, verify, verify_csv
from scripts.p00_context import Snapshot

ROOT = Path(__file__).resolve().parents[2]


def test_exact_human_approved_patches_preserve_original_contracts():
    result = verify(ROOT)
    assert result["status"] == "EXACT_PATCH_ORIGINAL_CLAUSE_PRESERVATION_PASS"
    assert not result["accepted"] and not result["qualified_reading"]
    assert not result["runtime_conformance"] and not result["execution_eligible"]


@pytest.mark.parametrize("defect", ["predicate", "exception", "clause", "binding", "owner", "completion", "gate", "after_patch"])
def test_rehashed_candidate_cannot_omit_or_promote_original_obligations(defect):
    candidate = deepcopy(json.loads((ROOT / DECISION).read_text(encoding="utf-8")))
    if defect == "predicate": candidate["original_acceptance_predicates"].pop()
    if defect == "exception": candidate["closure_exceptions"].pop()
    if defect == "clause": candidate["closure_exceptions"][0]["original_clause"]["clause_sha256"] = "0" * 64
    if defect == "binding": candidate["untouched_original_sources"][0]["git_blob"] = "0" * 40
    if defect == "owner": candidate["closure_exceptions"][0]["status"] = "ACCEPTED"
    if defect == "completion": candidate["completion"]["R01_R08"] = "8/8"
    if defect == "gate": candidate["qualified_reading"] = True
    if defect == "after_patch": candidate["integration_grants"][0]["after_normalized_lf_sha256"]["scripts/p00_context.py"] = "0" * 64
    with pytest.raises(ValueError):
        verify(ROOT, candidate)


@pytest.mark.parametrize("defect", ["literal", "pointer", "value", "source", "delta_omit", "delta_promote"])
def test_csv_source_and_obligation_omission_cannot_be_rehashed_away(defect):
    decision = json.loads((ROOT / DECISION).read_text(encoding="utf-8"))
    report = json.loads((ROOT / "docs/program/reviews/P00-bottleneck-3492569/csv-review.json").read_text(encoding="utf-8"))
    delta = json.loads((ROOT / "automation/platform/source_reading_obligations.csv-a.delta.v1.json").read_text(encoding="utf-8"))
    if defect == "literal": report["fixture_recommendation"]["ten_column_utf8_LF"] = report["fixture_recommendation"]["nine_column_utf8_LF"]
    if defect == "pointer": report["fixture_hash_binding"]["Q01_pointer_bindings"].pop("/cases/0/input/mapping")
    if defect == "value": report["fixture_hash_binding"]["Q01_pointer_bindings"]["/cases/0/input/coverage"]["value_sha256_compact_sorted_UTF8_LF"] = "0" * 64
    if defect == "source": decision["CSV_EXACT_WORK_PACKAGE"]["source_pins"][0]["sha256"] = "0" * 64
    if defect == "delta_omit": delta["affected_obligation_ids"].pop()
    if defect == "delta_promote": delta["actual_reading_verified"] = True
    with pytest.raises(ValueError):
        verify_csv(ROOT, Snapshot(ROOT, decision["review_subject"]), decision, report, delta)
