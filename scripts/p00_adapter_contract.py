"""P00 DTO/store 候選 coverage gate；只檢查設計與 pinned source，不授予權限。"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from p00_context import Snapshot, safe_path


MAP_PATH = "docs/architecture/contracts/dto_store_map.v1.json"


def canonical(value):
    """固定有限 JSON bytes；不容許 NaN/Infinity 混入 source fingerprint。"""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def validate_mapping(mapping, specs, source_snapshot):
    """對全部 schemas 與 exact Git blob/class 驗證；不證明 adapter 或語意 acceptance。"""
    if (mapping["status"] != "CANDIDATE_NOT_ACCEPTED" or mapping["authority"] != "NONE_DESIGN_ONLY"
            or mapping["runtime_implemented"] is not False or mapping["independent_review"] != "NOT_PERFORMED"):
        raise ValueError("CANDIDATE_CANNOT_ASSERT_RUNTIME_OR_ACCEPTANCE")
    schemas = specs[0]["components"]["schemas"]
    if any(spec["components"]["schemas"] != schemas for spec in specs[1:]):
        raise ValueError("SHARED_DTO_SCHEMA_DRIFT")
    rows = mapping["mappings"]
    names = [row["schema"] for row in rows]
    if len(names) != len(set(names)) or set(names) != set(schemas):
        raise ValueError("DTO_COVERAGE_MISSING_EXTRA_OR_DUPLICATE")
    required = {"kind", "semantic_owner", "store", "identity", "transaction", "restore", "reject",
                "implementation_package", "adapter_state"}
    used = set()
    for row in rows:
        if hashlib.sha256(canonical(schemas[row["schema"]])).hexdigest() != row["schema_sha256"]:
            raise ValueError("DTO_MAPPING_SCHEMA_MATERIAL_CHANGED")
        name = row["mapping_group"]
        if name not in mapping["groups"]:
            raise ValueError("MAPPING_OWNER_MISSING")
        used.add(name)
        group = mapping["groups"][name]
        if set(group) != required or any(not isinstance(value, str) or not value for value in group.values()):
            raise ValueError("MAPPING_CONTRACT_INCOMPLETE")
        if group["kind"] not in {"VALUE", "COMMAND", "PROJECTION", "IMMUTABLE", "MUTABLE", "ENVELOPE"}:
            raise ValueError("MAPPING_KIND_UNKNOWN")
        if group["adapter_state"] != "NOT_IMPLEMENTED_NOT_QUALIFIED":
            raise ValueError("ADAPTER_QUALIFICATION_NOT_ESTABLISHED")
    if used != set(mapping["groups"]):
        raise ValueError("UNUSED_MAPPING_GROUP")
    field_sources = mapping["new_record_field_sources"]
    if set(field_sources) != {"Signal", "Decision", "RiskDecision", "CapitalState", "IncrementalState", "TradingEvidenceEnvelope"}:
        raise ValueError("NEW_RECORD_FIELD_COVERAGE_MISSING")
    for name, fields in field_sources.items():
        schema = schemas[name]
        properties = schema.get("properties") or schema["oneOf"][0]["properties"]
        if set(fields) != set(properties) or any(not isinstance(value, str) or not value for value in fields.values()):
            raise ValueError("NEW_RECORD_FIELD_SOURCE_INCOMPLETE")
    if source_snapshot.baseline != mapping["source_master"]:
        raise ValueError("SOURCE_MASTER_MISMATCH")
    paths = set()
    for binding in mapping["source_bindings"]:
        path = safe_path(binding["source_path"])
        if path in paths or binding["baseline_sha"] != source_snapshot.baseline:
            raise ValueError("SOURCE_BINDING_DUPLICATE_OR_STALE")
        paths.add(path)
        raw, evidence = source_snapshot.read(path)
        if evidence["git_blob"] != binding["git_blob"] or evidence["sha256"] != binding["sha256"]:
            raise ValueError("SOURCE_BINDING_BLOB_MISMATCH")
        classes = {node.name for node in ast.walk(ast.parse(raw.decode("utf-8-sig")))
                   if isinstance(node, ast.ClassDef)}
        if not binding["source_classes"] or not set(binding["source_classes"]) <= classes:
            raise ValueError("SOURCE_BINDING_CLASS_MISSING")
    return {"status": "CANDIDATE_STRUCTURE_PASS", "schemas": len(names), "mapping_groups": len(used),
            "new_record_fields": sum(len(fields) for fields in field_sources.values()),
            "source_files": len(paths), "authority": "NONE", "adapter_conformance": "NOT_IMPLEMENTED",
            "independent_review": "NOT_PERFORMED", "execution_eligible": False}


def main():
    root = Path(__file__).resolve().parents[1]
    mapping = json.loads((root / MAP_PATH).read_text(encoding="utf-8"))
    specs = [json.loads((root / safe_path(path)).read_text(encoding="utf-8"))
             for path in mapping["schema_sources"]]
    result = validate_mapping(mapping, specs, Snapshot(root, mapping["source_master"]))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
