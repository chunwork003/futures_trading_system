"""Context V2 離線架構 probe：exact stage projection／omission oracle；不啟用 gate。"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import yaml
try:
    from p00_context import Snapshot, canonical, resolve
    from p00_context_pack import MARKER, project_openapi, encode_document, expand_json
    from p00_reading_obligations import RULES, source_document
except ModuleNotFoundError:
    from scripts.p00_context import Snapshot, canonical, resolve
    from scripts.p00_context_pack import MARKER, project_openapi, encode_document, expand_json
    from scripts.p00_reading_obligations import RULES, source_document

MANIFEST = "automation/governance/master_manifest.v1.yaml"
API_ROOT = "docs/architecture/contracts/"
STAGES = {
    "P01.CSV": {"rules": ["P01-CSV", "P01-REF"], "schemas": ["ImportMetadata", "DatasetMappingSnapshot"], "paths": []},
    "P01.IDENTITY": {"rules": ["P01-FRAME", "P01-FILE"], "schemas": ["DatasetManifest", "DatasetVersion", "DatasetPublicationResult"], "paths": []},
    "P01.QUALITY": {"rules": ["P01-COVERAGE", "P01-QUALITY", "P01-CORRECTION", "P01-TERMINAL", "P01-CASES"], "schemas": ["DatasetQualityReport", "DatasetCoverageRequest"], "paths": []},
    "P02.AUTH": {"rules": ["P02-HOST", "P02-ISOLATION", "P02-ACTOR", "P02-CASES"], "schemas": [], "paths": ["/auth/csrf", "/auth/login", "/auth/session", "/auth/logout"]},
    "P02.IMPORT": {"rules": ["P02-ISOLATION", "P02-WORKLOAD", "P02-WORKER", "P01-CSV", "P01-REF"], "schemas": [], "paths": ["/api/v1/dataset-imports"]},
    "P02.OPERATION": {"rules": ["P02-ISOLATION", "P02-WORKLOAD", "P02-WORKER"], "schemas": [], "paths": ["/api/v1/operations/{id}", "/api/v1/operations/{id}/cancel"]},
}
INVARIANT_IDS = {
    "PROVIDER_ACTUAL_DENIAL_WINS": "PROVIDER_DENIAL",
    "NO_AUTHORITY_CREATION": "NO_AUTHORITY",
    "HISTORICAL_PHASE_SNAPSHOT != CURRENT_LIFECYCLE_PROJECTION": "HISTORY_IS_NOT_CURRENT",
    "CONTRADICTORY_CURRENT_PROJECTION_FAIL_CLOSED_RECONCILIATION_REQUIRED": "CONTRADICTION_STOP",
    "REVIEW_PASS != INTEGRATION_PASS != MATERIALIZED_ACCEPTANCE": "DISTINCT_GATES",
    "IVF01_BLOCKED_UNTIL_REVIEWED_1_2_ACTIVATION_THEN_REV1_STALE": "IVF01_ACTIVATION",
    "AUTO_IMP_003_NOT_AUTHORIZED": "AUTO_IMP_003_DENIED",
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def node(snapshot, ident, path, value, selector, always=False):
    return {"id": ident, "source": snapshot.read(path)[1], "selector": selector,
            "value": value, "value_sha256": sha(canonical(value)), "always": always}

def section(snapshot, ident, path, heading, always=False):
    found = [u for u in source_document(snapshot, path)["units"] if u["selector"] == heading]
    if len(found) != 1:
        raise ValueError("AMBIGUOUS_OBLIGATION_SOURCE")
    unit = found[0]
    lines = snapshot.read(path)[0].decode("utf-8").splitlines(keepends=True)
    value = "".join(lines[unit["start_line"] - 1:unit["end_line"]])
    return node(snapshot, ident, path, value, heading, always)

def build_graph(root, baseline, package):
    """原 resolver universe 全量 retention；selected graph 尚未完成 semantic qualification。"""
    snapshot = Snapshot(root, baseline)
    package_path = "docs/program/packages/" + package + ".candidate.v1.json"
    spec = snapshot.read_json(package_path)
    request = {"task_type": "WORK", "package_id": package, "changed_paths": spec["authority"]["exact_scope"],
               "architecture_domains": ["program"], "baseline_sha": baseline}
    original = resolve(root, request)
    manifest = snapshot.read_json(MANIFEST)
    bindings = [b for b in manifest["policies"].values() if b.get("active") is True]
    bindings.append(manifest["negative_assertions"])
    if bindings[-1].get("active") is not True:
        raise ValueError("NEGATIVE_SOURCE_NOT_ACTIVE")
    nodes = []
    for path in ["AGENTS.md", "automation/work_orders/CURRENT_CODEX.yaml", "automation/work_orders/CURRENT_CODEX_TASK.md",
                 "automation/prompts/WORK_ORCHESTRATOR_KERNEL.md", package_path]:
        raw, _ = snapshot.read(path)
        try:
            value = json.loads(raw)
        except ValueError:
            value = raw.decode("utf-8")
        nodes.append(node(snapshot, "CONTROL:" + path, path, value, "FULL", True))
    for path in ["docs/CURRENT_STATE.md", "docs/CURRENT_WORK.md"]:
        lines = snapshot.read(path)[0].decode("utf-8").splitlines(keepends=True)
        boundary = next((i for i, line in enumerate(lines) if line.rstrip("\r\n") == MARKER), None)
        if boundary is None or boundary == 0:
            raise ValueError("AMBIGUOUS_CURRENT_BOUNDARY")
        nodes.append(node(snapshot, "CONTROL:" + path, path, "".join(lines[:boundary]), "EXPLICIT_CURRENT_PREFIX", True))
    # Active binding/navigation 投影待審；歷史 manifest 完整保留，不以此當 current grant。
    keys = ["schema_version", "manifest_id", "master_architecture_version", "status", "canonical_current_state", "policies", "negative_assertions"]
    nodes.append(node(snapshot, "CONTROL:ACTIVE_BINDINGS", MANIFEST, {k: manifest[k] for k in keys}, keys, True))
    for binding in {b["path"]: b for b in bindings}.values():
        raw, ref = snapshot.read(binding["path"])
        if ref["sha256"] != binding["sha256"]:
            raise ValueError("ACTIVE_POLICY_HASH_MISMATCH")
        nodes.append(node(snapshot, "POLICY:" + binding["path"], binding["path"], raw.decode("utf-8"), "FULL", True))
    for ident, packages, kind, path, heading, interpretation in RULES:
        cross_owner = package == "P02" and ident in STAGES["P02.IMPORT"]["rules"]
        if packages == "BOTH" or packages == package or cross_owner:
            nodes.append(section(snapshot, "SEM:" + ident, path, heading, packages == "BOTH"))
    negative_path = manifest["negative_assertions"]["path"]
    negative = yaml.safe_load(snapshot.read(negative_path)[0])
    if set(negative["invariants"]) != set(INVARIANT_IDS):
        raise ValueError("UNREVIEWED_INVARIANT_SET")
    negative_ids = ["NEG:" + v for v in negative["semantics"]["denied"]]
    negative_ids += ["INV:" + INVARIANT_IDS[v] for v in negative["invariants"]]
    retained = {r["path"]: r for r in original["mandatory_context"]}
    retained.update({n["source"]["path"]: n["source"] for n in nodes})
    return {"schema_version": "p00.context_v2_probe.graph.v1", "status": "UNREVIEWED_EXPERIMENT_ONLY",
            "baseline": baseline, "package": package, "request": request, "nodes": nodes,
            "retained_sources": list(retained.values()), "unconditional_negative_ids": negative_ids,
            "original_gate": original["context_budget"], "authority": "NONE", "execution_eligible": False,
            "qualification": "NOT_ESTABLISHED_FULL_UNCLASSIFIED_SOURCE_REMAINS_REVIEW_OBLIGATION"}

def capsule(graph, stage, root, profile="FULL_CONTROL"):
    if profile not in {"FULL_CONTROL", "CONTRACT_REVIEW_NO_EFFECTS"}:
        raise ValueError("UNKNOWN_STAGE_PROFILE")
    if stage not in STAGES or not stage.startswith(graph["package"] + "."):
        raise ValueError("CROSS_PACKAGE_OR_UNKNOWN_STAGE")
    selected = {"SEM:" + r for r in STAGES[stage]["rules"]}
    if selected - {n["id"] for n in graph["nodes"]}:
        raise ValueError("STAGE_OBLIGATION_MISSING")
    payload = [deepcopy(n) for n in graph["nodes"] if n["always"] or n["id"] in selected]
    deferred = []
    if profile == "CONTRACT_REVIEW_NO_EFFECTS":
        # 此 profile 僅供無效果的契約比對；行動／重新進入階段仍必須載入
        # 完整 WORK、current order、容量／成本來源與 fresh trusted intake。
        procedural = {"CONTROL:automation/prompts/WORK_ORCHESTRATOR_KERNEL.md",
                      "CONTROL:automation/work_orders/CURRENT_CODEX.yaml",
                      "CONTROL:automation/work_orders/CURRENT_CODEX_TASK.md",
                      "POLICY:automation/policies/execution_capacity_policy.v2_2.yaml",
                      "POLICY:automation/telemetry/execution_cost_contract.v2.yaml",
                      "POLICY:automation/specs/work_cost_accounting.v2.yaml"}
        deferred = [n["source"] for n in payload if n["id"] in procedural]
        payload = [n for n in payload if n["id"] not in procedural]
    snapshot = Snapshot(root, graph["baseline"])
    pool = {}
    for owner in ["python", "bff"]:
        path = API_ROOT + owner + ".openapi.v1.json"
        source = snapshot.read_json(path)
        wanted = STAGES[stage]["paths"]
        paths = [p for p in wanted if p in source["paths"]]
        if set(wanted) - source["paths"].keys() and not (stage == "P02.AUTH" and owner == "python"):
            raise ValueError("UNKNOWN_STAGE_ENDPOINT")
        value, closure = project_openapi(source, {"paths": paths, "schemas": STAGES[stage]["schemas"]})
        item = node(snapshot, "API:" + owner, path, value, {"paths": paths, "schemas": STAGES[stage]["schemas"]})
        if profile == "CONTRACT_REVIEW_NO_EFFECTS":
            packed = encode_document(path, canonical(value), pool)
            if expand_json(packed, pool) != value:
                raise ValueError("PROJECTION_RECONSTRUCTION_FAILURE")
            item["value"] = packed
            item["value_sha256"] = sha(canonical(packed))
        item["closure"] = closure
        payload.append(item)
    return {"schema_version": "p00.context_v2_probe.capsule.v1", "status": "UNREVIEWED_EXPERIMENT_ONLY",
            "baseline": graph["baseline"], "package": graph["package"], "stage": stage,
            "changed_paths": graph["request"]["changed_paths"], "documents": payload,
            "profile": profile, "schema_pool": pool, "deferred_preflight_sources": deferred,
            "deferred_rule": "REENTRY_OR_ANY_EFFECT_MUST_LOAD_ALL_DEFERRED_SOURCES_AND_REVALIDATE;_NO_TRUSTED_HANDOFF_ESTABLISHED",
            "negative_ids": graph["unconditional_negative_ids"], "authority": "NONE", "execution_eligible": False,
            "full_source_fallback": "UNKNOWN_RELEVANCE_SCOPE_DRIFT_CONTRADICTION_CROSS_OWNER_HISTORY_OR_STOP_REQUIRES_FRESH_REENTRY",
            "qualification": "CANDIDATE_PROJECTION_NOT_READING_RECEIPT_OR_CONTEXT_V2_GATE"}

def omission_oracle(root, baseline, package, stage, supplied, *, stop=False, profile="FULL_CONTROL"):
    """從來源重建 expectation，不能只信 supplied 自報的 hash/ids。"""
    if stop:
        raise ValueError("STOP_REQUIRES_REENTRY")
    expected = capsule(build_graph(root, baseline, package), stage, root, profile)
    if canonical(expected) != canonical(supplied):
        raise ValueError("OMISSION_STALE_SCOPE_OR_SOURCE_DRIFT")
    return "EXACT_PROJECTION_ONLY_SEMANTIC_REVIEW_AND_INJECTION_NOT_ASSERTED"

def probe(root, baseline, output=None, profile="FULL_CONTROL"):
    rows = []
    for package in ["P01", "P02"]:
        graph = build_graph(root, baseline, package)
        if output:
            Path(output, package + ".graph.json").write_bytes(canonical(graph) + b"\n")
        for stage in STAGES:
            if not stage.startswith(package + "."):
                continue
            value = capsule(graph, stage, root, profile)
            raw = canonical(value) + b"\n"
            if output:
                Path(output, stage + ".capsule.json").write_bytes(raw)
            rows.append({"stage": stage, "profile": profile, "capsule_bytes_including_envelope": len(raw), "capsule_sha256": sha(raw),
                         "retained_source_bytes": sum(r["size_bytes"] for r in graph["retained_sources"]),
                         "original_aggregate_bytes": graph["original_gate"]["mandatory_bytes"],
                         "experimental_stage_target_met": len(raw) <= 131072,
                         "actual_injected_bytes": None, "token_count": None, "reading_qualification": "NOT_RUN",
                         "original_gate": "FAIL_UNCHANGED"})
    return {"status": "ARCHITECTURE_PROBE_NON_AUTHORITY", "source_candidate": baseline,
            "loaded_probe_sha256": sha(Path(__file__).read_bytes()), "stages": rows,
            "scope": "6_REPRESENTATIVE_STAGES_NOT_FULL_PACKAGE_OR_LAUNCH_QUALIFICATION", "profile": profile,
            "compiler_resolver_policy_changed": False, "execution_eligible": False}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--output-dir", help="Experimental graphs/capsules only; never receipts/policies")
    parser.add_argument("--profile", choices=["FULL_CONTROL", "CONTRACT_REVIEW_NO_EFFECTS"], default="FULL_CONTROL")
    args = parser.parse_args()
    if args.output_dir:
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    print(json.dumps(probe(args.root, args.baseline, args.output_dir, args.profile), ensure_ascii=False, indent=2))
