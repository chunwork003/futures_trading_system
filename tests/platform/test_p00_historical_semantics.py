"""有界歷史source／scope bridge反例，不將source labels當新acceptance。"""

import copy
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from p00_context import Snapshot, safe_path
from p00_historical_semantics import span, source_blocks, verify

REGISTRY=json.loads((ROOT/"docs/program/historical_semantic_bridge.v1.json").read_text(encoding="utf-8"))
CANDIDATE=Snapshot(ROOT,REGISTRY["source_candidate"])
MASTER=Snapshot(ROOT,REGISTRY["source_master"])


def test_actual_source_bridge_preserves_separate_scopes_and_pending_semantics():
    result=verify(REGISTRY,CANDIDATE,MASTER)
    assert result["master_source_files"]==8 and result["gap_source_rows"]==24
    assert result["status_reconciliations"]==4 and result["scope_bridges"]==4 and result["future_gates"]==6
    assert result["unselected_nonblank_lines"]>0 and result["full_semantic_coverage"]=="INCOMPLETE"
    assert result["new_v1_credit"]==0 and result["execution_eligible"] is False
    assert result["product_completion"]=="UNCALIBRATED" and result["independent_review"]=="NOT_PERFORMED"
    source_labels={r["id"]:r["source_columns"]["Status"] for r in REGISTRY["gap_source_rows"]}
    assert source_labels["GAP-BROKER-001"]=="CLOSED"
    assert source_labels["GAP-07-MARGIN-001"]=="PARTIAL"
    assert source_labels["GAP-LIVE-001"]=="OPEN"


def test_all_nonblank_source_bytes_have_exact_ordered_block_coverage_not_semantic_acceptance():
    for doc in REGISTRY["source_documents"]:
        raw,evidence=MASTER.read(doc["source_ref"]["path"])
        assert evidence==doc["source_ref"]
        lines=raw.splitlines(keepends=True)
        selected=[]; previous=0
        for block in doc["blocks"]:
            a,b=block["first_line"],block["last_line"]
            assert a>previous and all(l.strip() for l in lines[a-1:b])
            content=b"".join(lines[a-1:b])
            assert hashlib.sha256(content).hexdigest()==block["sha256"]
            selected.extend(lines[a-1:b]);previous=b
        assert b"".join(selected)==b"".join(l for l in lines if l.strip())
        assert doc["selected_nonblank_lines"]+doc["unselected_nonblank_lines"]==doc["nonblank_line_count"]
        assert doc["semantic_review"]=="SELECTED_CLAUSES_ONLY_PENDING_INDEPENDENT_REVIEW"


@pytest.mark.parametrize("mutate",[
    lambda x:x.update(authority="AUTHORIZED"),
    lambda x:x.update(status="ACCEPTED"),
    lambda x:x.update(new_v1_credit=False),
    lambda x:x.update(revision=True),
    lambda x:x.update(execution_eligible=True),
    lambda x:x.update(independent_review="PASS"),
    lambda x:x.update(actual_runtime_verification="PASS"),
    lambda x:x.update(product_completion=1),
    lambda x:x.update(current_writer="P00"),
    lambda x:x["source_documents"].pop(),
    lambda x:x["source_documents"][0]["source_ref"].update(sha256="0"*64),
    lambda x:x["source_documents"][1]["blocks"].pop(),
    lambda x:x["source_documents"][1]["blocks"][0].update(first_line=2),
    lambda x:x["coverage"].update(full_product_requirement_coverage="COMPLETE"),
    lambda x:x["coverage"].update(outside_universe="NONE"),
    lambda x:x["coverage"].update(unselected_nonblank_lines=0),
    lambda x:x["selected_clauses"].pop(),
    lambda x:x["selected_clauses"][0]["source"].update(last_line=20),
    lambda x:x["selected_clauses"][0]["source"].update(sha256="0"*64),
    lambda x:x["selected_clauses"][0].update(new_v1_credit=151),
    lambda x:x["selected_clauses"][0].update(existing_delta_ids=["NEW-UNAUTHORIZED"]),
    lambda x:x["selected_clauses"][2].update(integration="VERIFIED_RUNTIME"),
    lambda x:x["selected_clauses"][2]["candidate_evidence"].update(git_blob="0"*40),
    lambda x:x["gap_source_rows"].pop(),
    lambda x:x["gap_source_rows"][0]["source_columns"].update(Status="READY"),
    lambda x:x["status_reconciliations"][0].update(accepted_source_modified=True),
    lambda x:x["status_reconciliations"][0].update(selected_evidence_clause_id="A2-OLD-STATUS"),
    lambda x:x["scope_bridges"][0].update(status="ACCEPTED_NEW_SCOPE"),
    lambda x:x["scope_bridges"][0]["candidate_source"].update(first_line=1),
    lambda x:x["scope_bridges"][1].update(existing_delta_ids=["P11-OPERATIONS"]),
    lambda x:x["future_dependencies"].pop(),
    lambda x:x["future_dependencies"][0].update(gate="WAIVED_BY_SIMULATED_V1"),
    lambda x:x["future_dependencies"][1].update(verification="PG_VERIFIED"),
    lambda x:x["future_dependencies"][2].update(execution_authority="GRANTED"),
    lambda x:x["primary_index_preservation"].update(source_files=30),
    lambda x:x["primary_index_preservation"]["source_ref"].update(sha256="0"*64),
    lambda x:x["delta_ledger_preservation"].update(status="NEW_WEIGHT_ACCEPTED"),
    lambda x:x["remaining"].clear(),
])
def test_omission_false_completeness_future_waiver_and_acceptance_promotion_are_rejected(mutate):
    registry=copy.deepcopy(REGISTRY);mutate(registry)
    with pytest.raises(ValueError,match="SOURCE_SCOPE_OR_PROPOSAL_MISMATCH"):
        verify(registry,CANDIDATE,MASTER)


@pytest.mark.parametrize("key",["source_master","source_candidate"])
def test_source_snapshot_cannot_drift_silently(key):
    registry=copy.deepcopy(REGISTRY);registry[key]="0"*40
    with pytest.raises(ValueError,match="BASELINE_MISMATCH"):
        verify(registry,CANDIDATE,MASTER)


@pytest.mark.parametrize("a,b",[(0,1),(2,1),(1,100000),(True,2),(1,False)])
def test_source_ranges_are_positive_exact_integers(a,b):
    with pytest.raises(ValueError,match="SOURCE_RANGE_INVALID"):
        span(MASTER,"docs/BACKTEST_ENGINE.md",a,b)


@pytest.mark.parametrize("path",["../secret","data/private.json",".git/config","/absolute","C:/outside.json"])
def test_cli_source_path_cannot_read_data_secret_or_outside_root(path):
    with pytest.raises(ValueError):safe_path(path)


def test_primary_index_and_delta_are_exact_read_only_predecessor_bindings():
    for field in ("primary_index_preservation","delta_ledger_preservation"):
        ref=REGISTRY[field]["source_ref"];raw,actual=CANDIDATE.read(ref["path"])
        assert ref==actual
        assert (ROOT/ref["path"]).read_bytes().replace(b"\r\n",b"\n")==raw.replace(b"\r\n",b"\n")
    assert len({r["id"] for r in REGISTRY["selected_clauses"]})==len(REGISTRY["selected_clauses"])
    assert all(r["gate"]=="PRESERVED_NOT_WAIVED" for r in REGISTRY["future_dependencies"])
