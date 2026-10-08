"""歷史 scope 的完整來源保留與假 acceptance／重複計分反例。"""

import copy
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from p00_context import Snapshot
from p00_requirements import expand_maps, owner_sections, table_rows, verify

REGISTRY = json.loads((ROOT / "docs/program/historical_requirements.v1.json").read_text(encoding="utf-8"))
LEDGER = json.loads((ROOT / "docs/program/program_baseline.v1.json").read_text(encoding="utf-8"))
CANDIDATE = Snapshot(ROOT, REGISTRY["candidate_snapshot"])
MASTER = Snapshot(ROOT, LEDGER["source_master"])


def test_actual_source_universe_preserves_request_capabilities_leaves_and_separate_acceptance_scopes():
    result = verify(REGISTRY, LEDGER, CANDIDATE, MASTER)
    assert (result["owner_sections"], result["owner_source_blocks"], result["capabilities"]) == (91, 922, 92)
    assert result["owner_explicit_clauses"] == 143
    assert (result["blueprint_leaves"], result["blueprint_historical_weight"]) == (603, 2137)
    assert (result["recorded_acceptance_events"], result["recorded_acceptance_unique_leaves"],
            result["recorded_acceptance_historical_weight"]) == (6, 76, 323)
    assert result["new_v1_credit"] == 0 and result["execution_eligible"] is False
    assert result["product_completion"] == "UNCALIBRATED"
    # 269 ACCEPTED labels／852 weight 屬歷史 metrics；六個 source event 不冒充完整 intake。
    labelled = [r for r in REGISTRY["blueprint_leaves"] if r["historical_lifecycle_label"] == "ACCEPTED"]
    assert (len(labelled), sum(r["historical_weight"] for r in labelled)) == (269, 852)
    assert REGISTRY["acceptance_events"][-1]["disposition_field"] == "ACCEPTED_SCOPE_LIST_NO_PASS_FIELD"


def test_all_original_nonblank_bytes_and_full_section_boundaries_are_preserved():
    raw = CANDIDATE.read("docs/program/P00_OWNER_REQUEST.md")[0]
    lines = raw.splitlines(keepends=True)
    cursor = REGISTRY["owner_preamble"]["last_line"]
    for section in REGISTRY["owner_sections"]:
        pointer = section["source"]
        assert pointer["first_line"] == cursor + 1
        body = b"".join(lines[cursor:pointer["last_line"]])
        assert hashlib.sha256(body).hexdigest() == pointer["sha256"]
        block_bytes = b"".join(b"".join(lines[b["source"]["first_line"] - 1:b["source"]["last_line"]])
                               for b in section["source_blocks"])
        assert block_bytes == b"".join(line for line in body.splitlines(keepends=True) if line.strip())
        cursor = pointer["last_line"]
    assert cursor == len(lines)


def test_blueprint_range_maps_keep_every_original_capability_consumer():
    leaves = {r["id"]: r for r in REGISTRY["blueprint_leaves"]}
    assert leaves["D710"]["maps_raw"] == "D01-D05"
    assert leaves["D710"]["capability_ids"] == ["D01", "D02", "D03", "D04", "D05"]
    assert leaves["I810"]["capability_ids"] == ["I01", "I02", "I03", "I04"]


def test_explicit_obligations_keep_non_goals_skill_evaluation_and_six_journey_aliases_distinct():
    from collections import Counter
    assert Counter(row["group"] for row in REGISTRY["owner_clause_catalog"]) == {
        "V1-MUST": 32, "V1-NONGOAL": 10, "JOURNEY": 6, "SKILL": 22,
        "GOLDEN": 9, "DELIVERABLE": 45, "OUTPUT": 19}
    routes = {r["id"]: r for r in REGISTRY["owner_clause_routes"]}
    assert [routes[f"OWNER-021-JOURNEY-{i:02}"]["journeys"] for i in range(1, 7)] == [
        ["J2"], ["J3"], ["J4"], ["J5"], ["J6"], ["J1"]]
    assert all(routes[r["id"]]["obligation"] == "EVALUATE_REUSE_GAP_NOT_CREATE_ALL"
               for r in REGISTRY["owner_clause_catalog"] if r["group"] == "SKILL")


def test_source_index_additions_do_not_promote_predecessor_owner_coverage_dispositions():
    previous = CANDIDATE.read_json("docs/program/request_coverage.v1.json")
    current = json.loads((ROOT / "docs/program/request_coverage.v1.json").read_text(encoding="utf-8"))
    assert len(current["requirements"]) == 91
    for old, new in zip(previous["requirements"], current["requirements"]):
        assert {key: new[key] for key in old} == old
        assert new["source_index"]["requirement_id"] == f"OWNER-{old['section']:03}"
        assert new["source_index"]["source_status"] == "EXACT_SOURCE_INDEXED_NOT_SEMANTICALLY_ACCEPTED"


@pytest.mark.parametrize("value", ["D05-D01", "D01-I05", "D01-D99,D01", "D01-D03,D02", "D01-05", "UNKNOWN"])
def test_ambiguous_invalid_and_overlapping_map_ranges_are_rejected(value):
    with pytest.raises(ValueError, match="SOURCE_.*(INVALID|DUPLICATE)"):
        expand_maps(value)


def test_malformed_source_table_row_cannot_silently_disappear_from_denominator():
    raw = b"| ID | Name |\n|---|---|\n| A110 | valid |\n| A120 | missing end\n"
    with pytest.raises(ValueError, match="ROW_MALFORMED"):
        table_rows(raw, "docs/fixture.md", "| ID | Name |", 2)


def test_dropped_owner_section_fails_before_a_partial_inventory_can_be_called_complete():
    raw = b"preamble\n" + b"".join(f"# {i}. section\nbody\n".encode() for i in range(91) if i != 18)
    with pytest.raises(ValueError, match="SECTION_MISSING"):
        owner_sections(raw)


@pytest.mark.parametrize("mutation,reason", [
    ("source_drop", "source_evidence"), ("source_hash", "source_evidence"),
    ("owner_drop", "owner_sections"), ("block_drop", "owner_sections"),
    ("source_line", "owner_sections"), ("boolean_line", "owner_sections"),
    ("capability_drop", "capabilities"), ("leaf_drop", "blueprint_leaves"),
    ("leaf_weight", "blueprint_leaves"), ("lifecycle_promotion", "blueprint_leaves"),
    ("accepted_leaf_expansion", "acceptance_events"), ("fake_pass", "acceptance_events"),
    ("core_added", "TOTALS"), ("new_credit", "NOT_NEW_CREDIT"),
    ("source_complete_is_semantic_complete", "NOT_PRODUCT_ACCEPTANCE"),
    ("fake_accepted_field", "FIELDS"), ("owner_fake_accepted", "ROUTE_FIELDS"),
    ("missing_owner_route", "OWNER_ROUTE_MISSING"), ("missing_capability_route", "CAPABILITY_ROUTE_MISSING"),
    ("range_consumer_drop", "LEAF_CLOSURE"), ("unknown_delta", "DELTA_LINK"),
    ("missing_remaining", "SEMANTIC_CLOSURE"), ("index_blob", "INDEX_SOURCE"),
    ("core_scope_merge", "CORE_OVERLAP"), ("candidate_drift", "BASELINE"),
])
def test_missing_changed_fabricated_and_overlapping_scope_is_rejected(mutation, reason):
    value = copy.deepcopy(REGISTRY)
    if mutation == "source_drop":
        value["source_evidence"].pop()
    elif mutation == "source_hash":
        value["source_evidence"][0]["sha256"] = "0" * 64
    elif mutation == "owner_drop":
        value["owner_sections"].pop()
    elif mutation == "block_drop":
        value["owner_sections"][18]["source_blocks"].pop()
    elif mutation == "source_line":
        value["owner_sections"][0]["source"]["first_line"] += 1
    elif mutation == "boolean_line":
        value["owner_sections"][0]["source_blocks"][0]["source"]["last_line"] = True
    elif mutation == "capability_drop":
        value["capabilities"].pop()
    elif mutation == "leaf_drop":
        value["blueprint_leaves"].pop()
    elif mutation == "leaf_weight":
        value["blueprint_leaves"][0]["historical_weight"] += 113
    elif mutation == "lifecycle_promotion":
        next(r for r in value["blueprint_leaves"] if r["historical_lifecycle_label"] == "NOT_DESIGNED")["historical_lifecycle_label"] = "ACCEPTED"
    elif mutation == "accepted_leaf_expansion":
        value["acceptance_events"][0]["blueprint_leaves"].append("J710")
    elif mutation == "fake_pass":
        value["acceptance_events"][-1]["disposition_field"] = "EXPLICIT_PASS"
    elif mutation == "core_added":
        value["totals"]["blueprint_leaves"] += 26
        value["totals"]["blueprint_historical_weight"] += 113
    elif mutation == "new_credit":
        value["capability_routes"][0]["new_v1_credit"] = 1
    elif mutation == "source_complete_is_semantic_complete":
        value["semantic_reconciliation"] = "COMPLETE"
    elif mutation == "fake_accepted_field":
        value["accepted"] = True
    elif mutation == "owner_fake_accepted":
        value["owner_routes"][0]["accepted"] = True
    elif mutation == "missing_owner_route":
        value["owner_routes"].pop()
    elif mutation == "missing_capability_route":
        value["capability_routes"].pop()
    elif mutation == "range_consumer_drop":
        next(r for r in value["capability_routes"] if r["id"] == "D05")["blueprint_leaves"].remove("D710")
    elif mutation == "unknown_delta":
        value["capability_routes"][0]["delta_deliverables"] = ["LIVE-ACTIVATE"]
    elif mutation == "missing_remaining":
        value["owner_routes"][0]["remaining_semantic_check"] = ""
    elif mutation == "index_blob":
        value["candidate_index_evidence"][0]["git_blob"] = "0" * 40
    elif mutation == "core_scope_merge":
        value["accepted_core_index"]["scope"] = "MERGED_INTO_603_AND_NEW_V1_CREDIT"
    else:
        value["candidate_snapshot"] = MASTER.baseline
    with pytest.raises(ValueError, match=reason):
        verify(value, LEDGER, CANDIDATE, MASTER)


def test_altered_worktree_progress_ledger_is_not_the_pinned_planning_denominator():
    ledger = copy.deepcopy(LEDGER)
    ledger["deliverables"][0]["weight"] += 113
    with pytest.raises(ValueError, match="LEDGER_SOURCE_CHANGED"):
        verify(REGISTRY, ledger, CANDIDATE, MASTER)


@pytest.mark.parametrize("mutation,reason", [
    ("drop_non_goal", "EXACT_SOURCE_INDEX"), ("drop_deliverable", "CLAUSE_ROUTE_MISSING"),
    ("claimed_accepted", "NOT_ACCEPTANCE"), ("drop_golden_qualification", "EVALUATION_NOT_QUALIFIED"),
    ("mandatory_to_nongoal", "CANNOT_BECOME_NONGOAL"), ("journey_duplicate", "NOT_BIJECTIVE"),
    ("unknown_skill", "REFERENCE_INVALID"), ("extra_credit", "NOT_ACCEPTANCE"),
])
def test_atomic_obligation_cannot_be_lost_reclassified_or_credited(mutation, reason):
    value = copy.deepcopy(REGISTRY)
    if mutation == "drop_non_goal":
        value["owner_clause_catalog"] = [r for r in value["owner_clause_catalog"] if r["group"] != "V1-NONGOAL"]
    elif mutation == "drop_deliverable":
        value["owner_clause_routes"] = [r for r in value["owner_clause_routes"] if r["id"] != "OWNER-084-DELIVERABLE-45"]
    elif mutation == "claimed_accepted":
        value["owner_clause_routes"][0]["state"] = "ACCEPTED"
    elif mutation == "mandatory_to_nongoal":
        value["owner_clause_routes"][0]["state"] = "NO_V1_DELIVERY_COMMITMENT"
    elif mutation == "drop_golden_qualification":
        next(r for r in value["owner_clause_routes"] if "-GOLDEN-" in r["id"])["state"] = "PARTIAL_CANDIDATE_NOT_ACCEPTED"
    elif mutation == "journey_duplicate":
        next(r for r in value["owner_clause_routes"] if r["id"] == "OWNER-021-JOURNEY-01")["journeys"] = ["J1"]
    elif mutation == "unknown_skill":
        next(r for r in value["owner_clause_routes"] if "-SKILL-" in r["id"])["reuse_skill_ids"] = ["unqualified-new-agent"]
    else:
        value["owner_clause_routes"][0]["new_v1_credit"] = 113
    with pytest.raises(ValueError, match=reason):
        verify(value, LEDGER, CANDIDATE, MASTER)
