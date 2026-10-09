"""R06 閱讀計畫／聲明相容性 oracle；復用 resolver/packer，無 intake、寫入或授權。"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

try:
    from p00_context import Snapshot, bind_loaded_source, canonical, resolve
    from p00_context_pack import build_pack, expand_json
except ModuleNotFoundError:
    from scripts.p00_context import Snapshot, bind_loaded_source, canonical, resolve
    from scripts.p00_context_pack import build_pack, expand_json

TOOL = "scripts/p00_reading.py"
CONTRACT = "automation/platform/context_reading_contract.v1.json"
SCHEMA = "automation/platform/reading_claim.schema.v1.json"
TARGET = 131072


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def validate_shape(value, schema):
    Draft202012Validator.check_schema(schema)
    # JSON Schema integer 接受1.0；本契約要求真正 JSON integer，且排除 bool。
    consumer = value.get("consumer", value) if isinstance(value, dict) else None
    if not isinstance(consumer, dict) or type(consumer.get("continuity_epoch")) is not int:
        raise ValueError("INVALID_CONTINUITY_EPOCH")
    Draft202012Validator(schema).validate(value)


def make_plan(context, pack_raw, consumer, schema):
    """純函式檢查 representation closure；輸入來源真實性只由 bound wrapper 重建。"""
    validate_shape(consumer, schema["$defs"]["consumer"])
    if consumer["role"] != context["request"]["task_type"]:
        raise ValueError("CONSUMER_ROLE_MISMATCH")
    pack = json.loads(pack_raw)
    if (context.get("authority") != "NONE_CONTEXT_ONLY" or context.get("execution_eligible") is not False
            or pack.get("authority") != "NONE_READING_AID_ONLY" or pack.get("execution_eligible") is not False):
        raise ValueError("READING_CANNOT_GRANT_AUTHORITY")
    if (pack["request"] != context["request"] or pack["source_context_hash"] != context["context_hash"]
            or pack["source_baseline_sha"] != context["source_baseline_sha"]):
        raise ValueError("PACK_CONTEXT_MISMATCH")
    refs = {r["path"]: r for r in context["mandatory_context"]}
    if len(refs) != len(context["mandatory_context"]):
        raise ValueError("DUPLICATE_MANDATORY_SOURCE")
    obligations, seen = [], set()
    for document in pack["documents"]:
        ref = document["source"]
        path = ref["path"]
        if path in seen or path not in refs or canonical(ref) != canonical(refs[path]):
            raise ValueError("MANDATORY_REPRESENTATION_MISMATCH")
        seen.add(path)
        if document["format"] == "JSON":
            payload = canonical(expand_json(document, pack["schema_pool"]))
            mode = "JSON_PROJECTION" if "projection" in document else "FULL_JSON_VALUE"
        elif document["format"] in ("TEXT", "CURRENT_WITH_HISTORY_REFERENCE"):
            payload = document["text"].encode("utf-8")
            mode = "CURRENT_SECTION_WITH_HISTORY_REFERENCE" if document["format"] != "TEXT" else "FULL_TEXT"
        else:
            raise ValueError("UNKNOWN_READING_FORMAT")
        exclusions = deepcopy(document.get("projection", {}))
        if mode == "CURRENT_SECTION_WITH_HISTORY_REFERENCE":
            exclusions = {k: document[k] for k in ["archive_start_line", "history_marker_count", "archive_text_sha256", "archive_load_rule"]}
        obligations.append({"id": "read:" + path, "source": ref, "mode": mode,
                            "payload_sha256": hashlib.sha256(payload).hexdigest(),
                            "payload_bytes": len(payload), "exclusions": exclusions,
                            "semantic_discharge": "NOT_REVIEWED"})
    if seen != set(refs):
        raise ValueError("MISSING_MANDATORY_REPRESENTATION")
    original_bytes = sum(r["size_bytes"] for r in refs.values())
    if context["context_budget"]["mandatory_bytes"] != original_bytes or context["context_budget"]["target_max_bytes"] != TARGET:
        raise ValueError("ORIGINAL_BUDGET_MISMATCH")
    plan = {"schema_version": "p00.reading_plan.v1", "status": "CANDIDATE_NOT_QUALIFIED",
            "authority": "NONE_READING_AUDIT_ONLY", "execution_eligible": False,
            "consumer": deepcopy(consumer), "request": deepcopy(context["request"]),
            "source_baseline_sha": context["source_baseline_sha"], "source_context_hash": context["context_hash"],
            "pack_sha256": hashlib.sha256(pack_raw).hexdigest(), "obligations": obligations,
            "original_budget": {"mandatory_bytes": original_bytes, "target_max_bytes": TARGET,
                                "status": "WITHIN_TARGET" if original_bytes <= TARGET else "OVER_TARGET_REQUIRES_COMPACTION"},
            "representation_bytes": len(pack_raw), "representation_fits_target": len(pack_raw) <= TARGET,
            "source_validation": "NOT_PERFORMED_PURE_FUNCTION", "actual_reading_verified": False,
            "semantic_qualification": "NOT_PERFORMED", "current_intake_complete": False}
    plan["plan_hash"] = digest(plan)
    return plan


def audit_claims(plan, claims, consumer, schema):
    """檢查 session 與 exact payload 聲明；不把 caller 宣稱轉為 trusted read receipt。"""
    if not isinstance(claims, list):
        raise ValueError("CLAIMS_ARRAY_REQUIRED")
    if digest({k: v for k, v in plan.items() if k != "plan_hash"}) != plan.get("plan_hash"):
        raise ValueError("PLAN_HASH_MISMATCH")
    validate_shape(consumer, schema["$defs"]["consumer"])
    obligations = {o["id"]: o for o in plan["obligations"]}
    covered, seen, duplicates = set(), {}, 0
    for claim in claims:
        validate_shape(claim, schema)
        key = (digest(claim["consumer"]), claim["plan_hash"], claim["obligation_id"])
        value = canonical(claim)
        if key in seen:
            if seen[key] != value:
                raise ValueError("READING_CLAIM_CONFLICT")
            duplicates += 1
            continue
        seen[key] = value
        if claim["consumer"] != consumer or consumer != plan["consumer"]:
            raise ValueError("SESSION_OR_CONSUMER_CHANGED_REREAD")
        if claim["plan_hash"] != plan["plan_hash"]:
            raise ValueError("STALE_PLAN_REREAD")
        obligation = obligations.get(claim["obligation_id"])
        if obligation is None:
            raise ValueError("UNKNOWN_READING_OBLIGATION")
        if claim["payload_sha256"] != obligation["payload_sha256"]:
            raise ValueError("PAYLOAD_CHANGED_REREAD")
        covered.add(claim["obligation_id"])
    if consumer != plan["consumer"]:
        raise ValueError("SESSION_OR_CONSUMER_CHANGED_REREAD")
    return {"schema_version": "p00.reading_audit.v1", "plan_hash": plan["plan_hash"],
            "status": "ALL_PAYLOADS_CLAIMED_NOT_VERIFIED" if covered == set(obligations) else "MISSING_READING_CLAIMS",
            "claimed": sorted(covered), "missing": sorted(set(obligations) - covered), "duplicates": duplicates,
            "trust": "UNVERIFIED_CALLER_CLAIMS", "actual_reading_verified": False,
            "semantic_qualification": "NOT_PERFORMED", "current_intake_complete": False,
            "execution_eligible": False, "authority": "NONE_READING_AUDIT_ONLY",
            "remaining_gates": ["INDEPENDENT_OBLIGATION_SEMANTIC_REVIEW", "TRUSTED_RECEIPT_AND_CURRENT_REGISTRY",
                                "REPRESENTATIVE_GOLDEN_EVALUATION", "MANIFEST_SOURCE_COVERAGE", "ORIGINAL_TOTAL_CONTEXT_BUDGET",
                                "EXACT_MIGRATION_GRANT", "EXISTING_AUTHORITY_DEPENDENCY_WRITER_CAPACITY_GATES"]}


def governance_coverage(snapshot, context):
    """檢查manifest宣告的active來源；不把resolver清單等同完整governance義務。"""
    manifest = snapshot.read_json("automation/governance/master_manifest.v1.yaml")
    bindings = [b for b in manifest["policies"].values() if b.get("active") is True]
    negative = manifest.get("negative_assertions")
    if isinstance(negative, dict) and negative.get("active") is True:
        bindings.append(negative)
    refs, seen = [], set()
    for binding in bindings:
        ref = snapshot.read(binding["path"])[1]
        if ref["sha256"] != binding["sha256"]:
            raise ValueError("MANIFEST_SOURCE_HASH_MISMATCH")
        if ref["path"] not in seen:
            refs.append(ref)
            seen.add(ref["path"])
    mandatory = {r["path"]: r for r in context["mandatory_context"]}
    absent = [r for r in refs if r["path"] not in mandatory]
    for ref in refs:
        if ref["path"] in mandatory and canonical(ref) != canonical(mandatory[ref["path"]]):
            raise ValueError("MANIFEST_CONTEXT_SOURCE_MISMATCH")
    negative_known = isinstance(negative, dict) and negative.get("active") is True
    return {"status": "UNREPRESENTED_DECLARED_GOVERNANCE_SOURCES" if absent else
                      ("DECLARED_BINDINGS_REPRESENTED_NOT_QUALIFIED" if negative_known else "NEGATIVE_ASSERTIONS_BINDING_UNKNOWN"),
            "declared_source_refs": refs, "unrepresented_sources": absent,
            "unrepresented_source_bytes": sum(r["size_bytes"] for r in absent),
            "negative_assertions_binding": "SOURCE_HASH_VERIFIED" if negative_known else "UNKNOWN",
            "semantic_completeness": "NOT_ASSERTED", "current_intake_complete": False}


def inspect_bound(root, request, consumer, claims, observed_master):
    """snapshot/loaded source、full source 與 projection 重建；freshness 仍是呼叫端觀測。"""
    snapshot = Snapshot(root, request["baseline_sha"])
    binding = bind_loaded_source(snapshot, TOOL, __file__)
    contract = snapshot.read_json(CONTRACT)
    if (contract["status"] != "CANDIDATE_NON_AUTHORITY" or contract["budget"]["target_max_bytes"] != TARGET
            or contract["budget"]["basis"] != "ORIGINAL_TOTAL_MANDATORY_SOURCE_BYTES"
            or contract["budget"]["compiler_migration"] != "NOT_PERFORMED"):
        raise ValueError("UNSUPPORTED_READING_CONTRACT")
    context = resolve(root, request)
    # 驗證 exact SHA 存在；不接受 HEAD、短 SHA 或把呼叫端 SHA 說成網路 attestation。
    Snapshot(root, observed_master)
    if observed_master != context["source_baseline_sha"]:
        raise ValueError("MASTER_DRIFT_REENTRY_REQUIRED")
    pack_raw, _ = build_pack(root, request, selective=True)
    schema = snapshot.read_json(SCHEMA)
    plan = make_plan(context, pack_raw, consumer, schema)
    plan.update(source_validation="REGENERATED_EXACT_SOURCE_REVIEW_NOT_ASSERTED", tool_binding=binding,
                contract_binding=snapshot.read(CONTRACT)[1], schema_binding=snapshot.read(SCHEMA)[1],
                master_observation={"sha": observed_master, "freshness": "CALLER_REPORTED_NOT_ATTESTED"},
                governance_source_coverage=governance_coverage(snapshot, context))
    plan["plan_hash"] = digest({k: v for k, v in plan.items() if k != "plan_hash"})
    plan_bytes = len(canonical(plan)) + 1
    claim_bytes = len(canonical(claims)) + 1
    return {"plan": plan, "audit": audit_claims(plan, claims, consumer, schema),
            "carrier_metrics": {"pack_bytes": len(pack_raw), "plan_bytes": plan_bytes,
                                "claim_bytes": claim_bytes, "aggregate_bytes": len(pack_raw) + plan_bytes + claim_bytes,
                                "target_max_bytes": TARGET, "compiler_gate_changed": False,
                                "basis": "OBSERVATION_ONLY_NOT_ORIGINAL_GATE_REPLACEMENT"}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--request", required=True)
    parser.add_argument("--consumer", required=True)
    parser.add_argument("--claims")
    parser.add_argument("--observed-master", required=True)
    args = parser.parse_args()
    load = lambda p: json.loads(Path(p).read_text(encoding="utf-8-sig"))
    result = inspect_bound(args.root, load(args.request), load(args.consumer), load(args.claims) if args.claims else [], args.observed_master)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
