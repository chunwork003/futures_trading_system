"""P00 候選閱讀包：exact source、JSON schema 去重、明示歷史分離；不取代 re-entry。"""

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

try:
    from p00_context import Snapshot, bind_loaded_source, canonical, resolve
except ModuleNotFoundError:
    from scripts.p00_context import Snapshot, bind_loaded_source, canonical, resolve

PACKER_PATH = "scripts/p00_context_pack.py"
MARKER = "## HISTORICAL CURRENT PROJECTIONS BELOW — audit only, superseded by current section above"
HISTORY_PATHS = {"docs/CURRENT_STATE.md", "docs/CURRENT_WORK.md"}
SELECTION_PATH = "automation/platform/context_selection.v1.json"


def project_openapi(value, selection):
    """依明示 root 建立 schema closure；不以名稱猜測相依、不刪 root 的限制。"""
    schemas = value["components"]["schemas"]
    paths = selection["paths"]
    roots = selection["schemas"]
    if len(set(paths)) != len(paths) or len(set(roots)) != len(roots):
        raise ValueError("DUPLICATE_SELECTION")
    if set(paths) - value["paths"].keys() or set(roots) - schemas.keys():
        raise ValueError("UNKNOWN_SELECTION_ROOT")
    result = deepcopy(value)
    result["paths"] = {p: deepcopy(value["paths"][p]) for p in paths}
    result["components"].pop("schemas")
    needed = set(roots)

    def references(node):
        if isinstance(node, dict):
            if "$dynamicRef" in node or "$recursiveRef" in node:
                raise ValueError("UNSUPPORTED_REFERENCE")
            if "$ref" in node:
                ref = node["$ref"]
                prefix = "#/components/schemas/"
                if not isinstance(ref, str) or not ref.startswith(prefix):
                    if not isinstance(ref, str) or not ref.startswith("#/components/"):
                        raise ValueError("UNSUPPORTED_REFERENCE")
                    # 非 schema components 完整保留；核對目標存在，內容已在整體 traversal 內。
                    target = result
                    try:
                        for part in ref[2:].split("/"):
                            target = target[part.replace("~1", "/").replace("~0", "~")]
                    except (KeyError, TypeError):
                        raise ValueError("UNRESOLVED_COMPONENT_REFERENCE") from None
                else:
                    name = ref[len(prefix):]
                    if name not in schemas:
                        raise ValueError("UNRESOLVED_SCHEMA_REFERENCE")
                    needed.add(name)
            for item in node.values():
                references(item)
        elif isinstance(node, list):
            for item in node:
                references(item)

    # 保留 info/security/servers/extensions 與非 schema components；其 refs 也需閉合。
    references(result)
    scanned = set()
    while needed - scanned:
        name = sorted(needed - scanned)[0]
        references(schemas[name])
        scanned.add(name)
    result["components"]["schemas"] = {name: deepcopy(schemas[name]) for name in sorted(needed)}
    return result, {"selected_paths": paths, "schema_roots": roots,
                    "included_schemas": sorted(needed),
                    "excluded_paths": sorted(set(value["paths"]) - set(paths)),
                    "excluded_schemas": sorted(set(schemas) - needed),
                    "full_source_load_rule": "Load full exact source when scope, dependencies, review or contradictions require excluded contracts."}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encode_document(path, raw, pool):
    """僅共享 OpenAPI schema 全值；不刪除欄位、不推測未使用契約。"""
    text = raw.decode("utf-8-sig")
    if path.endswith((".json", ".yaml")):
        # 本平台的 machine YAML 為 JSON；非 JSON 時完整保留文字。
        try:
            value = json.loads(text)
        except ValueError:
            return {"format": "TEXT", "text": text}
        packed = deepcopy(value)
        shared = {}
        if isinstance(value, dict) and "openapi" in value and value.get("components", {}).get("schemas"):
            for name, schema in packed.get("components", {}).pop("schemas", {}).items():
                key = digest(canonical(schema))
                if key in pool and pool[key] != schema:
                    raise ValueError("SCHEMA_POOL_COLLISION")
                pool[key] = schema
                shared[name] = key
        return {"format": "JSON", "value": packed, "shared_schemas": shared,
                "semantic_sha256": digest(canonical(value))}
    if path in HISTORY_PATHS:
        lines = text.splitlines(keepends=True)
        matches = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == MARKER]
        if not matches:
            raise ValueError("AMBIGUOUS_HISTORY_BOUNDARY")
        position = matches[0]
        current, archive = "".join(lines[:position]), "".join(lines[position:])
        if not current.strip() or not archive.strip():
            raise ValueError("EMPTY_HISTORY_PARTITION")
        return {"format": "CURRENT_WITH_HISTORY_REFERENCE", "text": current,
                "archive_start_line": position + 1, "history_marker_count": len(matches),
                "archive_text_sha256": digest(archive.encode("utf-8")),
                "archive_load_rule": "Read full source for historical claims, unresolved contradictions, review or lifecycle provenance."}
    return {"format": "TEXT", "text": text}


def expand_json(document, pool):
    """供 reader／測試還原完整 JSON；缺 schema 或內容變更一律失敗。"""
    value = deepcopy(document["value"])
    if document["shared_schemas"]:
        schemas = {}
        for name, key in document["shared_schemas"].items():
            schema = pool[key]
            if digest(canonical(schema)) != key:
                raise ValueError("SCHEMA_POOL_HASH_MISMATCH")
            schemas[name] = deepcopy(schema)
        value.setdefault("components", {})["schemas"] = schemas
    if digest(canonical(value)) != document["semantic_sha256"]:
        raise ValueError("JSON_RECONSTRUCTION_MISMATCH")
    return value


def build_pack(root, request, selective=False):
    context = resolve(root, request)
    snapshot = Snapshot(root, request["baseline_sha"])
    binding = bind_loaded_source(snapshot, PACKER_PATH, __file__)
    pool, documents = {}, []
    selections = {}
    selection_evidence = None
    if selective:
        policy = snapshot.read_json(SELECTION_PATH)
        if policy["status"] != "CANDIDATE_READING_ONLY":
            raise ValueError("INVALID_SELECTION_POLICY")
        selections = policy["packages"][request["package_id"]]
        selection_evidence = snapshot.read(SELECTION_PATH)[1]
        mandatory_paths = {e["path"] for e in context["mandatory_context"]}
        if set(selections) - mandatory_paths:
            raise ValueError("SELECTION_OUTSIDE_CONTEXT")
    for evidence in context["mandatory_context"]:
        raw, actual = snapshot.read(evidence["path"])
        if actual != evidence:
            raise ValueError("SOURCE_EVIDENCE_MISMATCH")
        if actual["path"] in selections:
            projected, selection = project_openapi(json.loads(raw), selections[actual["path"]])
            documents.append({"source": actual, "projection": selection,
                              **encode_document(actual["path"], canonical(projected), pool)})
        else:
            documents.append({"source": actual, **encode_document(actual["path"], raw, pool)})
    for document in documents:
        if document["format"] == "JSON":
            expand_json(document, pool)
    pack = {"schema_version": "p00.context_reading_pack.v1", "status": "CANDIDATE_PENDING_REVIEW",
            "authority": "NONE_READING_AID_ONLY", "execution_eligible": False,
            "request": context["request"], "source_baseline_sha": context["source_baseline_sha"],
            "source_context_hash": context["context_hash"], "packer_binding": binding,
            "selection_policy": selection_evidence,
            "documents": documents, "schema_pool": pool,
            "optional_context": context["optional_context"],
            "forbidden_stale_context": context["forbidden_stale_context"],
            "limitations": ["Not a replacement for current authority resolution or latest result/delta intake.",
                            "Compiler full-source budget gate remains unchanged until independent review.",
                            "Explicitly marked history is referenced, not erased; load it for historical questions."]}
    raw = canonical(pack) + b"\n"
    metrics = {"schema_version": "p00.context_pack_metrics.v1", "pack_sha256": digest(raw),
               "source_context_hash": context["context_hash"],
               "source_mandatory_bytes": context["context_budget"]["mandatory_bytes"],
               "reading_pack_bytes": len(raw), "target_max_bytes": 131072,
               "size_target_met": len(raw) <= 131072,
               "execution_eligible": False, "review": "NOT_PERFORMED"}
    return raw, metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--metrics", required=True)
    parser.add_argument("--selective", action="store_true", help="候選明示 schema closure；不改 compiler gate")
    args = parser.parse_args()
    request = json.loads(Path(args.request).read_text(encoding="utf-8-sig"))
    raw, metrics = build_pack(args.root, request, selective=args.selective)
    Path(args.output).write_bytes(raw)
    Path(args.metrics).write_bytes(canonical(metrics) + b"\n")


if __name__ == "__main__":
    main()
