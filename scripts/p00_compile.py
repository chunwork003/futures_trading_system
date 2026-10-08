"""P00 package mechanical compiler：無 dispatch、無 authority、無 shell execution。"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

try:
    from p00_context import canonical, safe_path
except ModuleNotFoundError:
    from scripts.p00_context import canonical, safe_path

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
    if identity["baseline_sha"] != context["request"]["baseline_sha"]:
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
    output = {"schema_version": "p00.compiled_package.v1", "identity": identity,
        "status": "PACKAGE_NOT_READY" if reasons else "COMPILED_CANDIDATE_PENDING_INDEPENDENT_REVIEW",
        "not_ready_reasons": reasons, "context_hash": context["context_hash"],
        "package_hash": hashlib.sha256(canonical(package)).hexdigest(),
        "scope_hash": hashlib.sha256(canonical(scope)).hexdigest(),
        "schema_hash": hashlib.sha256(canonical(schema)).hexdigest(),
        "authority": "NONE_COMPILATION_ONLY", "execution_eligible": False,
        "unevaluated_gates": ["INDEPENDENT_SEMANTIC_REVIEW", "DEPENDENCY_ACCEPTANCE_SEMANTICS",
            "CURRENT_EXACT_AUTHORIZATION", "PROGRAM_WEIGHT_LEDGER", "PROVIDER_CAPACITY", "ONE_WRITER"],
        "package": package}
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True)
    parser.add_argument("--context", required=True)
    args = parser.parse_args()
    package = json.loads(Path(args.package).read_text(encoding="utf-8-sig"))
    context = json.loads(Path(args.context).read_text(encoding="utf-8-sig"))
    schema = json.loads((ROOT / "automation/platform/package.schema.v1.json").read_text(encoding="utf-8"))
    print(json.dumps(compile_candidate(package, context, schema), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
