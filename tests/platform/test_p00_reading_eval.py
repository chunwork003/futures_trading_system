"""真實 package 來源的 omission/continuity 規格評估；不能替代模型或durable race。"""
import hashlib
from pathlib import Path
import pytest
from scripts.p00_context import Snapshot, resolve, canonical
from scripts.p00_context_pack import build_pack
from scripts.p00_reading import make_plan, governance_coverage
from scripts.p00_reading_eval import exercise
ROOT=Path(__file__).resolve().parents[2]
BASE="36f6c0779227ea9a735d3650cad1d98ee8a2f19c"

@pytest.fixture(scope="module",params=["P01","P02"])
def evaluation(request):
    snap=Snapshot(ROOT,BASE)
    req={"task_type":"WORK","package_id":request.param,"changed_paths":snap.read_json("docs/program/packages/"+request.param+".candidate.v1.json")["authority"]["exact_scope"],"architecture_domains":["program"],"baseline_sha":BASE}
    context=resolve(ROOT,req); pack,_=build_pack(ROOT,req,selective=True)
    schema=snap.read_json("automation/platform/reading_claim.schema.v1.json")
    consumer={"role":"WORK","task_id":"spec-task","session_id":"spec-session","continuity_epoch":1}
    return context,pack,consumer,schema,governance_coverage(snap,context)


def test_real_package_omission_and_changed_context_are_denied(evaluation):
    result=exercise(*evaluation); cases={r["id"]:r for r in result["cases"]}
    for id in ["OMIT_SOURCE_DOCUMENT","DUPLICATE_SOURCE_DOCUMENT","PACK_CONTEXT_CHANGED","SCOPE_CHANGED","CHANGED_SESSION_ID","CHANGED_CONTINUITY_EPOCH","CONFLICT_FORWARD","CONFLICT_REVERSE"]:
        assert cases[id]["outcome"]=="EXPECTED_DENIAL_OBSERVED"
    assert cases["OMIT_ONE_CLAIM"]["missing_count"]==1
    assert cases["IDENTICAL_REPLAY"]["duplicates"]==1


def test_all_synthetic_claims_never_promote_trust_budget_or_race(evaluation):
    result=exercise(*evaluation); cases={r["id"]:r for r in result["cases"]}
    assert cases["ALL_CLAIMS_NOT_TRUST"]["trust"]=="UNVERIFIED_CALLER_CLAIMS"
    assert result["actual_reading_verified"] is result["current_intake_complete"] is result["execution_eligible"] is False
    assert result["context_gate"].startswith("NOT_PASSED")
    assert result["semantic_qualification"]=="NOT_PERFORMED"
    assert any(c["id"]=="DURABLE_REGISTRY_STOP_RACE" for c in result["unexercised"])
    missing=cases["ACTIVE_NEGATIVE_SOURCE_GAP"]["missing_sources"]
    assert any(s["path"]=="automation/specs/negative_assertions.v2.yaml" for s in missing)


def test_independently_removed_safety_text_cannot_be_trusted_by_pure_plan(evaluation):
    # 純plan可看見同shape payload卻不能驗Git source：重建wrapper及獨立語意審查不可省略。
    import json
    context,pack,consumer,schema,_=evaluation; mutated=json.loads(pack)
    document=next(d for d in mutated["documents"] if d["format"]=="TEXT")
    document["text"]="safety text deliberately omitted for adverse fixture\n"
    plan=make_plan(context,canonical(mutated),consumer,schema)
    assert plan["source_validation"]=="NOT_PERFORMED_PURE_FUNCTION"
    assert plan["semantic_qualification"]=="NOT_PERFORMED"
    assert plan["actual_reading_verified"] is False
    assert hashlib.sha256(canonical(mutated)).hexdigest()!=hashlib.sha256(pack).hexdigest()
