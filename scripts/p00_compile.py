"""P00 package mechanical compiler：無 dispatch、無 authority、無 shell execution。"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

try:
    from p00_context import canonical, safe_path, Snapshot, resolve, bind_loaded_source
except ModuleNotFoundError:
    from scripts.p00_context import canonical, safe_path, Snapshot, resolve, bind_loaded_source

ROOT = Path(__file__).resolve().parents[1]


def compile_candidate(package, context, schema):
    """結構與 exact context binding；語意 review/authority gate 仍由既有 WORK owner 決定。"""
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(package)
    if context.get("schema_version") != "p00.context_manifest.v1":
        raise ValueError("UNSUPPORTED_CONTEXT_MANIFEST")
    digest_input = {k: v for k, v in context.items() if k != "context_hash"}
    if hashlib.sha256(canonical(digest_input)).hexdigest() != context.get("context_hash"):
        raise ValueError("CONTEXT_HASH_MISMATCH")
    if context.get("execution_eligible") is not False or context.get("authority") != "NONE_CONTEXT_ONLY":
        raise ValueError("CONTEXT_CANNOT_GRANT_AUTHORITY")
    identity = package["identity"]
    if identity["baseline_sha"] != context.get("source_baseline_sha", context["request"]["baseline_sha"]):
        raise ValueError("BASELINE_MISMATCH")
    if identity["package_id"] != context["request"]["package_id"]:
        raise ValueError("PACKAGE_MISMATCH")
    scope = sorted(safe_path(p) for p in package["authority"]["exact_scope"])
    protected = {safe_path(p) for p in package["authority"]["protected_scope"]}
    if set(scope) & protected:
        raise ValueError("PROTECTED_SCOPE_OVERLAP")
    if scope != sorted(set(context["request"]["changed_paths"])):
        raise ValueError("CONTEXT_SCOPE_MISMATCH")
    evidence = {item["path"]: item for item in context["evidence_refs"]}
    for binding in package["dependencies"]["required_acceptances"]:
        path = safe_path(binding["path"])
        if path not in evidence or evidence[path]["sha256"] != binding["sha256"]:
            raise ValueError("DEPENDENCY_EVIDENCE_NOT_BOUND")
    reasons = []
    if package["design"]["status"] != "DEFINED_CANDIDATE":
        reasons.append("DESIGN_NOT_DEFINED")
    if package["design"]["public_semantic_gaps"]:
        reasons.append("PUBLIC_SEMANTIC_GAPS")
    if context.get("context_budget", {}).get("status") != "WITHIN_TARGET":
        reasons.append("CONTEXT_COMPACTION_REQUIRED")
    if package["dependencies"]["external_gates"]:
        reasons.append("EXTERNAL_GATES_REQUIRE_EVALUATION")
    if package["dependencies"].get("required_packages") and not package["dependencies"]["required_acceptances"]:
        reasons.append("DEPENDENCY_ACCEPTANCE_NOT_BOUND")
    output = {"schema_version": "p00.compiled_package.v1", "identity": identity,
        "status": "PACKAGE_NOT_READY" if reasons else "COMPILED_CANDIDATE_PENDING_INDEPENDENT_REVIEW",
        "not_ready_reasons": reasons, "context_hash": context["context_hash"],
        "package_hash": hashlib.sha256(canonical(package)).hexdigest(),
        "scope_hash": hashlib.sha256(canonical(scope)).hexdigest(),
        "schema_hash": hashlib.sha256(canonical(schema)).hexdigest(),
        "provenance_validation": "NOT_PERFORMED_PURE_MECHANICAL_FUNCTION",
        "authority": "NONE_COMPILATION_ONLY", "execution_eligible": False,
        "unevaluated_gates": ["INDEPENDENT_SEMANTIC_REVIEW", "DEPENDENCY_ACCEPTANCE_SEMANTICS",
            "CURRENT_EXACT_AUTHORIZATION", "PROGRAM_WEIGHT_LEDGER", "PROVIDER_CAPACITY", "ONE_WRITER"],
        "package": package}
    return output


def compile_bound(root, package, context):
    """從 Git 重新取得 context；拒絕自行重算 hash 的偽造輸入。Package 是明示 authoring input。"""
    snapshot = Snapshot(root, context["request"]["baseline_sha"])
    binding = bind_loaded_source(snapshot, "scripts/p00_compile.py", __file__)
    fresh_context = resolve(root, context["request"])
    if canonical(fresh_context) != canonical(context):
        raise ValueError("CONTEXT_REHYDRATION_MISMATCH")
    policy = snapshot.read_json("automation/platform/context_policy.v1.json")
    package_path = policy["packages"][package["identity"]["package_id"]]["package_path"]
    if package_path.endswith(".json") and canonical(snapshot.read_json(package_path)) != canonical(package):
        raise ValueError("PACKAGE_SOURCE_SNAPSHOT_MISMATCH")
    for reference in package["design"]["input_output_schemas"]:
        path, separator, pointer = reference.partition("#")
        value = snapshot.read_json(safe_path(path))
        if separator:
            if not pointer.startswith("/"):
                raise ValueError("SCHEMA_JSON_POINTER_REQUIRED")
            try:
                for part in pointer[1:].split("/"):
                    key = part.replace("~1", "/").replace("~0", "~")
                    value = value[int(key)] if isinstance(value, list) else value[key]
            except (KeyError, IndexError, ValueError, TypeError) as exc:
                raise ValueError("SCHEMA_REFERENCE_NOT_FOUND") from exc
    schema_path = "automation/platform/package.schema.v1.json"
    result = compile_candidate(package, fresh_context, snapshot.read_json(schema_path))
    result.update(provenance_validation="SNAPSHOT_AND_LOADED_SOURCE_MATCH_REVIEW_NOT_ASSERTED",
                  compiler_binding=binding, schema_binding=snapshot.read(schema_path)[1])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True)
    parser.add_argument("--context", required=True)
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()
    package = json.loads(Path(args.package).read_text(encoding="utf-8-sig"))
    context = json.loads(Path(args.context).read_text(encoding="utf-8-sig"))
    print(json.dumps(compile_bound(args.root, package, context), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
