"""R06 exact source-to-reading義務候選；完整來源fallback、負面斷言與衝突不省略。"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re

import yaml

try:
    from p00_context import Snapshot, canonical, resolve, bind_loaded_source, safe_path
    from p00_context_pack import build_pack, expand_json
    from p00_intake import observe
except ModuleNotFoundError:
    from scripts.p00_context import Snapshot, canonical, resolve, bind_loaded_source, safe_path
    from scripts.p00_context_pack import build_pack, expand_json
    from scripts.p00_intake import observe

TOOL = "scripts/p00_reading_obligations.py"
NEGATIVE = "automation/specs/negative_assertions.v2.yaml"
API = "docs/architecture/V1_API_ARCHITECTURE.md"
BASE = "docs/architecture/V1_BASELINE.md"
CONTRACTS = "docs/architecture/V1_CONTRACTS.md"
IDENTITY = "docs/architecture/V1_DATASET_IDENTITY_IO.md"
QUALITY = "docs/architecture/V1_DATASET_QUALITY.md"
AUTH = "docs/architecture/V1_GENESIS_AUTH_CONTRACT.md"
HOST = "docs/architecture/V1_APPLICATION_BUILD_TESTHOST.md"
STATE = "docs/architecture/V1_STATE_MACHINES.md"
# 明確source section，不以標題相似度猜測或裁切安全prose。
RULES = [
 ("COMMON-SCOPE", "BOTH", "PROTECTED_SEMANTICS", BASE, "## 1. Product / scope", "BACKTEST/SIMULATED；P00未accepted/exact grant不得product implementation"),
 ("COMMON-MONEY", "BOTH", "POSITIVE_AND_NEGATIVE", BASE, "## 4. Money / time / identity", "finite Decimal/UTC/calendar/identity；float、日期猜測、修正版silent switch拒絕"),
 ("COMMON-OWNERS", "BOTH", "PROTECTED_SEMANTICS", BASE, "## 2. Cross-layer / ownership", "單一domain owner及薄adapter；BFF/UI不得建立經濟或恢復truth"),
 ("COMMON-CUT", "BOTH", "PROTECTED_SEMANTICS", BASE, "## 6. Runtime / strategy / decision / risk", "required cohort/current cut、risk減少仍驗authority；EXIT-confirm FLAT-re-evaluate-ENTER"),
 ("COMMON-COMPAT", "BOTH", "PROTECTED_SEMANTICS", CONTRACTS, "## Compatibility acceptance", "accepted models/legacy next-bar/cost/identity保留；新wire不替代domain constructor"),
 ("COMMON-DATA", "BOTH", "POSITIVE_AND_NEGATIVE", CONTRACTS, "## Data / strategy contracts", "immutable reference/data identity及quality語意，不把snapshot當canonical acceptance"),
 ("COMMON-RECEIPT", "BOTH", "POSITIVE_AND_NEGATIVE", API, "## Command linearization and retry", "exact key/body/revision replay、CAS、unknown response；不用new key重做"),
 ("COMMON-ERROR", "BOTH", "POSITIVE_AND_NEGATIVE", API, "## Queries, errors and audit", "auth/permission/errors、artifact/access/hash、upload safety；CSV矛盾不得省略"),
 ("COMMON-SHAPE", "BOTH", "NEGATIVE_ASSERTION", API, "## Validation boundary", "schema/hash/source match非currentness、broker/provenance或semantic acceptance"),
 ("COMMON-GENESIS", "BOTH", "PROTECTED_SEMANTICS", AUTH, "## Reservation is not an account", "reservation不等於account；missing genesis不可FLAT/READY；fence/atomic closure"),
 ("COMMON-AUTH", "BOTH", "POSITIVE_AND_NEGATIVE", AUTH, "## Exact BFF authentication routes", "cookie/CSRF/Origin/service身份、expiry/revocation、redaction；不能信UI/header"),
 ("COMMON-SYSTEM-AUTH", "BOTH", "NEGATIVE_ASSERTION", API, "## Two surfaces, one domain owner", "兩個listener身份不同；Python私有credential、BFF actor stripping、TLS驗證"),
 ("COMMON-STATE", "BOTH", "PROTECTED_SEMANTICS", STATE, "## Development lifecycle（既有accepted語意保留）", "consumed/invoked/resume/wake、review/integration/acceptance不同，不產生grant"),
 ("COMMON-READ", "BOTH", "READING_INTEGRITY", "automation/platform/CONTEXT_READING_RECEIPTS.md", "## Reading claim 與 continuity", "claim-only、同key衝突、source/scope/session/epoch失效重讀，不創造trusted ack"),
 ("COMMON-INTAKE", "BOTH", "INTAKE_DEPENDENCY", "automation/platform/CURRENT_INTAKE_REGISTRY_CONTRACT.md", "## Bootstrap / successor", "完整producer/current registry positive coverage未建立時UNKNOWN；既有WORK re-entry保留"),
 ("P01-FRAME", "P01", "POSITIVE_AND_NEGATIVE", IDENTITY, "## Hash framing v1", "exact framing/排序/既有mor1、semantic hash與raw file hash分離、correction lineage"),
 ("P01-CSV", "P01", "POSITIVE_AND_NEGATIVE", IDENTITY, "## CSV_V1", "十欄CSV_V1/source_code/可選檔首BOM/UTC Decimal bytes cap；禁止URL/path/sniffing/filler"),
 ("P01-REF", "P01", "POSITIVE_AND_NEGATIVE", IDENTITY, "## ReferenceSnapshotPort 候選介面", "pinned mapping/calendar/listed有效區間、owner/hash/ID一致，不讀DB猜coverage"),
 ("P01-FILE", "P01", "PROTECTED_SEMANTICS", IDENTITY, "## 發布與查詢引用鏈", "hash/framing/fsync/同filesystem atomic rename；stage非published、衝突不覆寫"),
 ("P01-COVERAGE", "P01", "POSITIVE_AND_NEGATIVE", QUALITY, "## 品質政策與 required coverage", "caller interval及完整calendar evidence；missing reference不變required=0、不猜夜盤日期"),
 ("P01-QUALITY", "P01", "POSITIVE_AND_NEGATIVE", QUALITY, "## 計數與判定優先序", "invalid/reference/missing/conflict/outside判定次序、完整immutable report，不信flag"),
 ("P01-CORRECTION", "P01", "PROTECTED_SEMANTICS", QUALITY, "## 更正 lineage 與 precedence", "完整新version；不混parent reference、不原地修補、不靠arrival/priority挑winner"),
 ("P01-TERMINAL", "P01", "POSITIVE_AND_NEGATIVE", QUALITY, "## Wire candidate 與剩餘 closure", "receipt/report跨record約束、null非0、cancel/infrastructure unknown不偽造terminal quality；P03 owner"),
 ("P01-CASES", "P01", "REQUIRED_EVIDENCE", QUALITY, "## 必要 golden cases", "Q01–Q10需actual importer/filesystem qualification；規格fixture不是runtime結果"),
 ("P02-HOST", "P02", "POSITIVE_AND_NEGATIVE", HOST, "## 建置矩陣與 lock ownership", "exact locks/native lanes、replay不重新解依賴；P11 container/install不冒充P02已驗證"),
 ("P02-ISOLATION", "P02", "PROTECTED_SEMANTICS", HOST, "## Production factory 與 test-host 隔離", "無durable adapter=503，auth先401/403；fake/provider/test credentials不入普通artifact"),
 ("P02-ACTOR", "P02", "PROTECTED_SEMANTICS", HOST, "## Identity / provider ownership 與交接", "trusted subject/session per-request；browser無URI/role/credential authority；redirect不轉secret"),
 ("P02-CASES", "P02", "REQUIRED_EVIDENCE", HOST, "## U01-U08 與 build acceptance", "auth/session/503/CSRF/cookie/artifact/unknown retry/LIVE拒絕；實際host/browser尚未run"),
 ("P02-WORKLOAD", "P02", "POSITIVE_AND_NEGATIVE", API, "## Fixed workload policy v1", "limits不可caller override；missing config拒絕、不宣稱throughput或partial success"),
 ("P02-WORKER", "P02", "PROTECTED_SEMANTICS", STATE, "## Research / workers", "operation/attempt/lease states、cancel/publish CAS、expiry holder不能成功，P03 durable owner"),
 ("P02-SIM", "P02", "PROTECTED_SEMANTICS", STATE, "## Trading / simulation", "非P02經濟implementation；kill非flat、MATCH/VALID不等於READY/permission"),
]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_document(snapshot, path):
    raw, ref = snapshot.read(path)
    text = raw.decode("utf-8")
    units = []
    if path.endswith(".md"):
        lines = text.splitlines(keepends=True)
        starts = sorted({0, *[i for i, line in enumerate(lines) if re.match(r"^#{1,6} ", line)]})
        occurrences = Counter()
        for i, start in enumerate(starts):
            end = starts[i + 1] if i + 1 < len(starts) else len(lines)
            title = lines[start].rstrip("\r\n") if re.match(r"^#{1,6} ", lines[start]) else "PREAMBLE"
            occurrences[title] += 1
            key = path + "\0" + title + "\0" + str(occurrences[title])
            units.append({"id": "section:" + sha(key.encode())[:20], "selector": title,
                          "occurrence": occurrences[title], "start_line": start + 1, "end_line": end,
                          "source_slice_sha256": sha("".join(lines[start:end]).encode("utf-8")),
                          "reading_rule": "FULL_EXACT_SECTION_NO_SAFETY_TRUNCATION"})
        assert "".join(lines).encode("utf-8") == raw
    elif path.endswith((".json", ".yaml")):
        value = yaml.safe_load(text)
        for key, child in sorted(value.items()):
            pointer = "/" + key.replace("~", "~0").replace("/", "~1")
            units.append({"id": "pointer:" + sha((path + "\0" + pointer).encode())[:20], "selector": pointer,
                          "value_sha256": sha(canonical(child)), "reading_rule": "FULL_SELECTED_VALUE_WITH_NESTED_CONSTRAINTS"})
    else:
        units.append({"id": "full:" + sha(path.encode())[:20], "selector": "FULL_SOURCE", "source_slice_sha256": sha(raw),
                      "reading_rule": "FULL_EXACT_SOURCE"})
    return {"source": ref, "units": units, "full_source_fallback": True,
            "unit_index_completeness": "COMPLETE_FOR_PINNED_BYTES", "semantic_qualification": "NOT_PERFORMED"}


def build_registry(candidate, master):
    root, baseline = candidate.root, candidate.baseline
    def package_context(pid):
        package = candidate.read_json("docs/program/packages/" + pid + ".candidate.v1.json")
        request = {"task_type": "WORK", "package_id": pid, "changed_paths": package["authority"]["exact_scope"],
                   "architecture_domains": ["program"], "baseline_sha": baseline}
        context = resolve(root, request)
        pack, metrics = build_pack(root, request, selective=True)
        return pid, context, json.loads(pack), metrics
    with ThreadPoolExecutor(max_workers=2) as pool:
        profiles = dict((p, (c, v, m)) for p, c, v, m in pool.map(package_context, ["P01", "P02"]))
    status = candidate.read_json("docs/program/p00_status.v1.json")
    supplements = {NEGATIVE, "automation/platform/CONTEXT_READING_RECEIPTS.md", "automation/platform/context_reading_contract.v1.json",
                   "automation/platform/reading_claim.schema.v1.json", "automation/platform/CURRENT_INTAKE_REGISTRY_CONTRACT.md",
                   "automation/platform/result_reading_index.v1.json", "automation/platform/intake_observation.schema.v1.json",
                   status["current_checkpoint_evidence"], status["focused_review_packet"]}
    result_index = candidate.read_json("automation/platform/result_reading_index.v1.json")
    supplements.update(r["source"]["path"] for r in result_index["records"])
    mandatory = {r["path"] for c, _, _ in profiles.values() for r in c["mandatory_context"]}
    sources = {p: source_document(candidate, p) for p in sorted(mandatory | supplements)}
    obligations = []
    for ident, packages, kind, path, selector, interpretation in RULES:
        matched = [u for u in sources[path]["units"] if u["selector"] == selector]
        if len(matched) != 1:
            raise ValueError("EXACT_SECTION_NOT_UNIQUE: " + path + " " + selector)
        obligations.append({"id": ident, "packages": ["P01", "P02"] if packages == "BOTH" else [packages],
                            "kind": kind, "source_path": path, "source_unit": matched[0]["id"],
                            "candidate_interpretation": interpretation, "status": "MAPPED_CANDIDATE_NOT_ACCEPTED"})
    negative = yaml.safe_load(candidate.read(NEGATIVE)[0])
    for i, denied in enumerate(negative["semantics"]["denied"]):
        obligations.append({"id": "NEG-" + denied, "packages": ["P01", "P02"], "kind": "NEGATIVE_ASSERTION",
                            "source_path": NEGATIVE, "json_pointer": "/semantics/denied/" + str(i),
                            "value_sha256": sha(canonical(denied)), "candidate_interpretation": "DENY " + denied,
                            "status": "ACTIVE_SOURCE_MAPPED_NOT_REPRESENTED_BY_ORIGINAL_RESOLVER"})
    for i, invariant in enumerate(negative["invariants"]):
        obligations.append({"id": "INV-" + str(i + 1), "packages": ["P01", "P02"], "kind": "PROTECTED_SEMANTICS",
                            "source_path": NEGATIVE, "json_pointer": "/invariants/" + str(i),
                            "value_sha256": sha(canonical(invariant)), "candidate_interpretation": invariant,
                            "status": "ACTIVE_SOURCE_MAPPED_NOT_REPRESENTED_BY_ORIGINAL_RESOLVER"})
    reports = {}
    for pid, (context, pack, metrics) in profiles.items():
        schema_units, endpoint_units = [], []
        for document in pack["documents"]:
            if document["source"]["path"].endswith(".openapi.v1.json"):
                value = expand_json(document, pack["schema_pool"])
                path = document["source"]["path"]
                for name, schema in sorted(value["components"]["schemas"].items()):
                    schema_units.append({"id": pid + ":" + path + ":schema:" + name,
                                         "source_path": path, "json_pointer": "/components/schemas/" + name,
                                         "value_sha256": sha(canonical(schema)), "kind": "POSITIVE_NEGATIVE_AND_SECURITY_CONSTRAINTS",
                                         "reading_rule": "FULL_VALUE_REQUIRED_RECURSIVE_REF_CLOSURE_NOT_SUMMARY"})
                for endpoint, body in sorted(value["paths"].items()):
                    endpoint_units.append({"id": pid + ":" + path + ":endpoint:" + endpoint,
                                           "source_path": path, "json_pointer": "/paths/" + endpoint.replace("~", "~0").replace("/", "~1"),
                                           "value_sha256": sha(canonical(body)), "reading_rule": "ALL_OPERATIONS_SECURITY_ERRORS_AND_REFS"})
        original = context["context_budget"]["mandatory_bytes"]
        extra = sum(candidate.read(p)[1]["size_bytes"] for p in supplements - {r["path"] for r in context["mandatory_context"]})
        reports[pid] = {"request": context["request"], "context_hash": context["context_hash"],
                        "mandatory_sources": [r["path"] for r in context["mandatory_context"]],
                        "mandatory_full_read_obligations": [{"id": pid + ":full:" + r["path"], "source": r,
                            "rule": "ALL_PINNED_SOURCE_OBLIGATIONS_REMAIN_MANDATORY_UNMAPPED_TEXT_NOT_WAIVED"} for r in context["mandatory_context"]],
                        "required_supplement_sources": sorted(supplements), "schema_reading_obligations": schema_units,
                        "endpoint_reading_obligations": endpoint_units,
                        "original_mandatory_bytes": original, "supplement_unique_bytes": extra,
                        "source_and_supplement_bytes": original + extra,
                        "selective_pack_bytes": metrics["reading_pack_bytes"], "target_max_bytes": 131072,
                        "source_excess_bytes": max(0, original - 131072),
                        "pack_excess_bytes": max(0, metrics["reading_pack_bytes"] - 131072),
                        "top_source_contributors": sorted(context["mandatory_context"], key=lambda r: (-r["size_bytes"], r["path"]))[:10],
                        "size_gate": "NOT_PASSED", "compiler_gate_changed": False,
                        "semantic_unit_mapping": "SELECTED_CRITICAL_RULES_PLUS_FULL_SOURCE_FALLBACK_NOT_EXHAUSTIVE_SEMANTIC_REVIEW"}
    api_units = [u for u in sources[API]["units"] if u["selector"] == "## Queries, errors and audit"]
    csv_units = [u for u in sources[IDENTITY]["units"] if u["selector"] == "## CSV_V1"]
    conflict = {"id": "R06-SOURCE-02", "priority": "P1", "handling": "HARD_BLOCK_AFFECTED_PUBLIC_CSV_SEMANTICS",
                "level": 3, "status": "ARCHITECT_DECISION_REQUIRED_NO_SOURCE_REWRITE",
                "packages": ["P01", "P02_UPLOAD_BOUNDARY"],
                "source_units": [api_units[0]["id"], csv_units[0]["id"]],
                "api_header": "instrument_id,contract_id,timeframe,bar_open_utc,open,high,low,close,volume",
                "csv_v1_header": "source_code,bar_open_utc,open,high,low,close,volume,amount,trade_count,tick_count",
                "bom_conflict": "API forbids BOM; dedicated CSV_V1 allows one leading BOM",
                "proposals": ["Align API prose/upload contract to explicit CSV_V1/P01 owner with exact reviewed amendment",
                              "If both formats intended, version explicit adapter/format contract; do not infer conversion"],
                "implementation": "NOT_AUTHORIZED", "original_candidate_public_semantic_gaps": "PRESERVED_AS_HISTORICAL_AUTHORING_NOT_CLAIMED_CURRENT_COMPLETE"}
    intake = observe(root, baseline, master.baseline)
    return {"schema_version": "p00.source_reading_obligations.v1", "status": "CANDIDATE_LOCAL_NOT_ACCEPTED",
            "source_candidate": baseline, "source_master": master.baseline,
            "generator_normalized_lf_sha256": sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n")),
            "source_documents": sources, "critical_semantic_obligations": obligations, "packages": reports,
            "source_findings": [{"id": "R06-SOURCE-01", "status": "MAPPED_SUPPLEMENT_ORIGINAL_RESOLVER_UNCHANGED",
                                 "path": NEGATIVE, "missing_is_none": False}, conflict],
            "result_dependencies": {"source_index": candidate.read("automation/platform/result_reading_index.v1.json")[1],
                                    "records": result_index["records"], "classification": "BOUND_PREDECESSOR_AND_HISTORICAL_COMPILATIONS_NOT_GLOBAL_CURRENT_REGISTRY",
                                    "latest_p00_checkpoint_at_snapshot": candidate.read(status["current_checkpoint_evidence"])[1],
                                    "latest_p00_review_at_snapshot": candidate.read(status["focused_review_packet"])[1]},
            "intake": intake, "reading_receipt": {"schema": candidate.read("automation/platform/reading_claim.schema.v1.json")[1],
                "complete_claims_generated": False, "actual_reading_verified": False, "trust": "UNVERIFIED",
                "reproduction": "Exact candidate/master/requests/loaded resolver+packer+intake; section/JSON hashes, no caller summary replacement",
                "invalidation": "Source/scope/session/epoch/registry head/STOP change requires re-entry; old raw claims remain historical"},
            "context_resolution_candidates": [{"id": "CTX-01", "proposal": "lossless JSON/schema byte dedup plus whole obligation proof", "state": "CURRENT_PACK_STILL_OVER_TARGET"},
                {"id": "CTX-02", "proposal": "Reviewed compact current/status projection, all authority bindings and histories/full-load triggers retained", "state": "NO_MIGRATION_GRANT"},
                {"id": "CTX-03", "proposal": "Stable semantic section IDs plus exact complete security/negative closure, independently review exclusions", "state": "THIS_MAP_IS_NOT_ACCEPTED_PROJECTION"},
                {"id": "CTX-04", "proposal": "If still impossible, explicit reviewed successor aggregate budget/continuity contract", "state": "NO_PER_BATCH_128KIB_CONVERSION"}],
            "completion": {"R06": "PARTIAL_REVIEW_PENDING", "P00_closed": 0, "P00_total": 8, "product_authorization": "NOT_AUTHORIZED",
                           "independent_review": "NOT_PERFORMED", "acceptance": False, "execution_eligible": False}}


def verify(registry, expected):
    if canonical(registry) != canonical(expected):
        raise ValueError("SOURCE_OBLIGATION_OR_PROTECTED_SEMANTICS_MISMATCH")
    return {"status": "EXACT_SOURCE_MAPPING_STRUCTURAL_PASS", "semantic_acceptance": "NOT_PERFORMED",
            "source_documents": len(registry["source_documents"]),
            "critical_obligations": len(registry["critical_semantic_obligations"]), "execution_eligible": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default="automation/platform/source_reading_obligations.v1.json")
    parser.add_argument("--tool-snapshot", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    registry = json.loads((root / safe_path(args.registry)).read_text(encoding="utf-8-sig"))
    binding = bind_loaded_source(Snapshot(root, args.tool_snapshot), TOOL, __file__)
    result = verify(registry, build_registry(Snapshot(root, registry["source_candidate"]), Snapshot(root, registry["source_master"])))
    print(json.dumps({**result, "tool_binding": binding}, ensure_ascii=False, indent=2))
