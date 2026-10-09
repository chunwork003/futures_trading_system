"""R06 repository-bound omission/continuity 規格 runner；無 durable receipt、模型評估或授權。"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from jsonschema import ValidationError
try:
    from p00_context import Snapshot, canonical, resolve, bind_loaded_source
    from p00_context_pack import build_pack
    import p00_reading as reading
except ModuleNotFoundError:
    from scripts.p00_context import Snapshot, canonical, resolve, bind_loaded_source
    from scripts.p00_context_pack import build_pack
    from scripts import p00_reading as reading
TOOL = "scripts/p00_reading_eval.py"


def exercise(context, pack_raw, consumer, schema, coverage):
    """只復用既有 oracle；synthetic claims 僅在記憶體內，不寫入 operational registry。"""
    plan = reading.make_plan(context, pack_raw, consumer, schema)
    claims = [{"schema_version":"p00.reading_claim.v1", "status":"CLAIM_ONLY", "consumer":deepcopy(consumer),
               "plan_hash":plan["plan_hash"], "obligation_id":o["id"], "payload_sha256":o["payload_sha256"]}
              for o in plan["obligations"]]
    if not claims:
        raise ValueError("REPRESENTATIVE_SOURCE_PLAN_EMPTY")
    rows = []
    def check(name, action, expected, error=False):
        try:
            result = action()
        except (ValueError, ValidationError) as exc:
            observed = "SCHEMA_REJECT" if isinstance(exc, ValidationError) else str(exc)
            if not error or expected not in observed:
                raise AssertionError(name + ": unexpected denial " + observed) from exc
            rows.append({"id":name, "outcome":"EXPECTED_DENIAL_OBSERVED", "reason":observed.splitlines()[0]})
            return
        if error or result["status"] != expected:
            raise AssertionError(name + ": expected outcome not observed")
        if any(result[k] is not False for k in ["actual_reading_verified","current_intake_complete","execution_eligible"]):
            raise AssertionError("SPEC_RESULT_CANNOT_PROMOTE_TRUST_OR_AUTHORITY")
        if result["semantic_qualification"] != "NOT_PERFORMED":
            raise AssertionError("SPEC_RESULT_CANNOT_SELF_QUALIFY")
        rows.append({"id":name, "outcome":"EXPECTED_UNVERIFIED_STATE_OBSERVED", "status":result["status"],
                     "missing_count":len(result["missing"]), "duplicates":result["duplicates"], "trust":result["trust"]})
    audit = lambda cs, p=plan, c=consumer: reading.audit_claims(p, cs, c, schema)
    check("EMPTY_CLAIMS", lambda:audit([]), "MISSING_READING_CLAIMS")
    check("ALL_CLAIMS_NOT_TRUST", lambda:audit(claims), "ALL_PAYLOADS_CLAIMED_NOT_VERIFIED")
    check("IDENTICAL_REPLAY", lambda:audit(claims+[deepcopy(claims[0])]), "ALL_PAYLOADS_CLAIMED_NOT_VERIFIED")
    check("OMIT_ONE_CLAIM", lambda:audit(claims[1:]), "MISSING_READING_CLAIMS")
    bad = {**claims[0],"payload_sha256":"f"*64}
    check("CONFLICT_FORWARD", lambda:audit([claims[0],bad]), "READING_CLAIM_CONFLICT", True)
    check("CONFLICT_REVERSE", lambda:audit([bad,claims[0]]), "PAYLOAD_CHANGED_REREAD", True)
    check("UNKNOWN_OBLIGATION", lambda:audit([{**claims[0],"obligation_id":"read:not-required.json"}]), "UNKNOWN_READING_OBLIGATION", True)
    check("PAYLOAD_CHANGED", lambda:audit([bad]), "PAYLOAD_CHANGED_REREAD", True)
    for field,value in [("task_id","spec-other-task"),("session_id","spec-other-session"),("continuity_epoch",consumer["continuity_epoch"]+1),("role","REVIEWER")]:
        changed = {**consumer,field:value}
        check("CHANGED_"+field.upper(), lambda c=changed:audit(claims,c=c), "SESSION_OR_CONSUMER_CHANGED_REREAD", True)
    changed = deepcopy(plan); changed["request"]["changed_paths"].append("storage/spec_unbound.py")
    changed["plan_hash"] = reading.digest({k:v for k,v in changed.items() if k!="plan_hash"})
    check("SCOPE_CHANGED", lambda:audit(claims,p=changed), "STALE_PLAN_REREAD", True)
    edit = deepcopy(plan); edit["original_budget"]["status"]="WITHIN_TARGET"
    check("UNREHASHED_PLAN_EDIT", lambda:audit(claims,p=edit), "PLAN_HASH_MISMATCH", True)
    pack = json.loads(pack_raw)
    omitted = deepcopy(pack); omitted["documents"].pop()
    check("OMIT_SOURCE_DOCUMENT", lambda:reading.make_plan(context,canonical(omitted),consumer,schema), "MISSING_MANDATORY_REPRESENTATION", True)
    duplicate = deepcopy(pack); duplicate["documents"].append(deepcopy(duplicate["documents"][0]))
    check("DUPLICATE_SOURCE_DOCUMENT", lambda:reading.make_plan(context,canonical(duplicate),consumer,schema), "MANDATORY_REPRESENTATION_MISMATCH", True)
    stale = deepcopy(pack); stale["source_context_hash"]="f"*64
    check("PACK_CONTEXT_CHANGED", lambda:reading.make_plan(context,canonical(stale),consumer,schema), "PACK_CONTEXT_MISMATCH", True)
    check("CLAIM_FAKE_AUTHORITY", lambda:audit([{**claims[0],"execution_eligible":True}]), "SCHEMA_REJECT", True)
    # source01 已明確缺少 negative assertions：規格 run 不得把它升格 represented/qualified。
    if coverage["status"] != "UNREPRESENTED_DECLARED_GOVERNANCE_SOURCES" or not any(r["path"]=="automation/specs/negative_assertions.v2.yaml" for r in coverage["unrepresented_sources"]):
        raise AssertionError("SOURCE01_EXPECTED_UNRESOLVED_BINDING_CHANGED_REVIEW_REQUIRED")
    rows.append({"id":"ACTIVE_NEGATIVE_SOURCE_GAP", "outcome":"KNOWN_SOURCE_GAP_STILL_OPEN", "missing_sources":coverage["unrepresented_sources"],"semantic_completeness":"NOT_ASSERTED"})
    rows.append({"id":"ORIGINAL_AGGREGATE_BUDGET", "outcome":"ORIGINAL_GATE_STILL_OVER_TARGET", "original_bytes":plan["original_budget"]["mandatory_bytes"], "pack_bytes":len(pack_raw), "target":131072})
    if plan["original_budget"]["status"]!="OVER_TARGET_REQUIRES_COMPACTION":
        raise AssertionError("BASELINE_BUDGET_CHANGED_REVIEW_REQUIRED")
    return {"cases":rows, "source_context_hash":context["context_hash"], "plan_hash":plan["plan_hash"],
            "pack_sha256":hashlib.sha256(pack_raw).hexdigest(), "mandatory_sources":len(plan["obligations"]),
            "source_validation":"BOUND_WRAPPER_REQUIRED", "synthetic_claims":"IN_MEMORY_SPEC_INPUT_ONLY_NOT_RECEIPTS",
            "original_mandatory_bytes":plan["original_budget"]["mandatory_bytes"], "selective_pack_bytes":len(pack_raw),
            "unexercised":[{"id":"DURABLE_REGISTRY_STOP_RACE","reason":"NO_TRUSTED_CURRENT_REGISTRY_BOOTSTRAP; sequence permutations above are not concurrency proof"},
                           {"id":"REAL_CONTEXT_LOSS_READING","reason":"NO_ACTUAL_MODEL_TASK_GOLDEN_RUN; synthetic consumer mutation is compatibility only"},
                           {"id":"SEMANTIC_OMISSION_COMPLETENESS","reason":"NO_INDEPENDENT_OBLIGATION_REVIEW; source equality and complete claims do not prove semantics"}],
            "actual_reading_verified":False,"current_intake_complete":False,"semantic_qualification":"NOT_PERFORMED",
            "execution_eligible":False,"context_gate":"NOT_PASSED_ORIGINAL_AGGREGATE_UNCHANGED"}


def run(root, planning, observed_master, tool_snapshot):
    snapshot = Snapshot(root, planning); tool = Snapshot(root,tool_snapshot)
    tool.git("merge-base","--is-ancestor",planning,tool_snapshot)
    binding = bind_loaded_source(tool,TOOL,__file__)
    def profile(pid):
        request={"task_type":"WORK","package_id":pid,"changed_paths":snapshot.read_json("docs/program/packages/"+pid+".candidate.v1.json")["authority"]["exact_scope"],"architecture_domains":["program"],"baseline_sha":planning}
        consumer={"role":"WORK","task_id":"spec-oracle-"+pid,"session_id":"spec-fixture-only","continuity_epoch":1}
        # 正式binding/contract check歸既有inspect_bound；此runner不複製或放寬規則。
        bound=reading.inspect_bound(root,request,consumer,[],observed_master)
        context=resolve(root,request)
        pack,_=build_pack(root,request,selective=True)
        schema=snapshot.read_json(reading.SCHEMA)
        result=exercise(context,pack,consumer,schema,bound["plan"]["governance_source_coverage"])
        if (result["pack_sha256"]!=bound["plan"]["pack_sha256"] or
                result["source_context_hash"]!=bound["plan"]["source_context_hash"]):
            raise ValueError("OWNER_RECONSTRUCTION_MISMATCH")
        result["source_refs"]=context["mandatory_context"]
        result["reading_owner_binding"]=bound["plan"]["tool_binding"]
        result["bound_empty_audit"]=bound["audit"]
        result["bound_carrier_metrics"]=bound["carrier_metrics"]
        result["source_validation"]="RECONSTRUCTED_PINNED_SOURCES_NOT_READING_ATTESTATION"
        return pid,result
    with ThreadPoolExecutor(max_workers=2) as pool:
        profiles=dict(pool.map(profile,["P01","P02"]))
    report={"schema_version":"p00.reading_spec_evaluation.v1","status":"REPOSITORY_BOUND_SPEC_EXERCISED_NOT_GOLDEN_QUALIFIED",
            "planning_snapshot":planning,"observed_master":observed_master,"tool_binding":binding,
            "contract_source":snapshot.read(reading.CONTRACT)[1],"schema_source":snapshot.read(reading.SCHEMA)[1],
            "packages":profiles,"authority":"NONE_OFFLINE_SPEC_EVIDENCE_ONLY","product_authorization":"NOT_AUTHORIZED",
            "independent_review":"NOT_PERFORMED","actual_model_golden":"NOT_RUN","durable_race_conformance":"NOT_RUN",
            "acceptance":False,"dispatch":False,"actual_reading_verified":False,"current_intake_complete":False,"execution_eligible":False}
    report["report_sha256"]=hashlib.sha256(canonical(report)).hexdigest()
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--planning-snapshot",required=True)
    parser.add_argument("--observed-master",required=True)
    parser.add_argument("--tool-snapshot",required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.root,args.planning_snapshot,args.observed_master,args.tool_snapshot),ensure_ascii=False,indent=2))
