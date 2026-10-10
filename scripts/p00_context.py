"""從 exact Git commit 建立 P00 context manifest；只讀、不授權、不 dispatch。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

POLICY = "automation/platform/context_policy.v1.json"
MASTER_MANIFEST = "automation/governance/master_manifest.v1.yaml"
RESOLVER_PATH = "scripts/p00_context.py"


class ContextError(ValueError):
    """context 不完整或有 unsafe/stale evidence；禁止默默 fallback。"""


def safe_path(path):
    if not isinstance(path, str) or not path or path.startswith(("/", "-")):
        raise ContextError("INVALID_REPOSITORY_PATH")
    if any(c in path for c in "\\:*?[]\x00\r\n") or any(ord(c) < 32 for c in path):
        raise ContextError("INVALID_REPOSITORY_PATH")
    parts = path.split("/")
    forbidden = {".git", ".codex", ".aws", ".ssh", "data", "secrets", "credentials"}
    for part in parts:
        lower = part.casefold()
        if part in ("", ".", "..") or part.endswith((" ", ".")) or lower in forbidden or lower.startswith(".env"):
            raise ContextError("FORBIDDEN_REPOSITORY_PATH")
    return path


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def bind_loaded_source(snapshot, path, loaded_file):
    """僅容許 Git/Windows 換行轉換；不將 source match 冒充獨立 review。"""
    raw, evidence = snapshot.read(path)
    loaded = Path(loaded_file).read_bytes()
    if raw.replace(b"\r\n", b"\n") != loaded.replace(b"\r\n", b"\n"):
        raise ContextError(f"LOADED_TOOL_SOURCE_MISMATCH: {path}")
    return {**evidence, "source_comparison": "EXACT_EXCEPT_CRLF_TRANSPORT", "review_status": "NOT_ASSERTED"}


class Snapshot:
    def __init__(self, root, baseline):
        if not isinstance(baseline, str) or not re.fullmatch(r"[0-9a-f]{40}", baseline):
            raise ContextError("EXACT_COMMIT_SHA_REQUIRED")
        self.root = Path(root)
        self.baseline = baseline
        self.cache = {}
        if self.git("cat-file", "-t", baseline).strip() != b"commit":
            raise ContextError("BASELINE_NOT_COMMIT")

    def git(self, *args):
        env = {**os.environ, "GIT_NO_REPLACE_OBJECTS": "1", "GIT_OPTIONAL_LOCKS": "0"}
        result = subprocess.run(["git", "--no-replace-objects", "-C", str(self.root), *args],
                                capture_output=True, env=env, check=False)
        if result.returncode:
            raise ContextError("GIT_EVIDENCE_UNAVAILABLE")
        return result.stdout

    def read(self, path):
        path = safe_path(path)
        if path not in self.cache:
            entry = self.git("ls-tree", "-z", self.baseline, "--", path)
            entries = [e for e in entry.split(b"\0") if e]
            if len(entries) != 1:
                raise ContextError(f"MISSING_EXACT_FILE: {path}")
            meta, actual = entries[0].split(b"\t", 1)
            mode, kind, blob = meta.decode("ascii").split(" ")
            if actual.decode("utf-8") != path or mode not in ("100644", "100755") or kind != "blob":
                raise ContextError(f"NON_REGULAR_CONTEXT_FILE: {path}")
            if int(self.git("cat-file", "-s", blob)) > 2 * 1024 * 1024:
                raise ContextError("CONTEXT_FILE_TOO_LARGE")
            raw = self.git("cat-file", "blob", blob)
            self.cache[path] = (raw, {"path": path, "baseline_sha": self.baseline,
                "git_blob": blob, "sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw)})
        return self.cache[path]

    def read_json(self, path):
        try:
            return json.loads(self.read(path)[0].decode("utf-8-sig"))
        except (ValueError, UnicodeError) as exc:
            raise ContextError(f"INVALID_JSON_EVIDENCE: {path}") from exc


def resolve(root, request):
    required_keys = {"task_type", "package_id", "changed_paths", "architecture_domains", "baseline_sha"}
    if not isinstance(request, dict) or set(request) != required_keys:
        raise ContextError("INVALID_CONTEXT_REQUEST_FIELDS")
    if not isinstance(request["changed_paths"], list) or not isinstance(request["architecture_domains"], list):
        raise ContextError("INVALID_CONTEXT_REQUEST_LISTS")
    if any(not isinstance(x, str) for x in request["architecture_domains"]):
        raise ContextError("INVALID_CONTEXT_DOMAIN")
    if not isinstance(request["task_type"], str) or not isinstance(request["package_id"], str):
        raise ContextError("INVALID_CONTEXT_IDENTITY")
    snapshot = Snapshot(root, request["baseline_sha"])
    policy = snapshot.read_json(POLICY)
    tool_binding = bind_loaded_source(snapshot, RESOLVER_PATH, __file__)
    source_baseline = policy.get("source_baseline_sha") or snapshot.baseline
    source = Snapshot(root, source_baseline)
    snapshot.git("merge-base", "--is-ancestor", source_baseline, snapshot.baseline)
    if policy.get("schema_version") != "p00.context_policy.v1" or policy.get("status") != "CANDIDATE_NON_AUTHORITY":
        raise ContextError("UNSUPPORTED_CONTEXT_POLICY")
    if request["task_type"] not in policy["task_types"]:
        raise ContextError("UNKNOWN_TASK_TYPE")
    if request["package_id"] not in policy["packages"]:
        raise ContextError("PACKAGE_NOT_REGISTERED")
    package = policy["packages"][request["package_id"]]
    paths = sorted({safe_path(p) for p in request["changed_paths"]})
    for path in paths:
        if path not in package["allowed_exact"] and not any(path.startswith(p) for p in package["allowed_prefixes"]):
            raise ContextError(f"PATH_OUTSIDE_PACKAGE_SCOPE: {path}")
    domains = set(request["architecture_domains"])
    for path in paths:
        for rule in policy["path_domains"]:
            if path.startswith(rule["prefix"]):
                domains.update(rule["domains"])
    if domains - policy["domains"].keys():
        raise ContextError("UNKNOWN_ARCHITECTURE_DOMAIN")
    mandatory = {POLICY, RESOLVER_PATH, MASTER_MANIFEST, package["package_path"], *policy["required"], *package["mandatory"],
                 *policy["role_context"][request["task_type"]]}
    for domain in domains:
        mandatory.update(policy["domains"][domain])
    optional = set(package["optional"]) - mandatory
    manifest = snapshot.read_json(MASTER_MANIFEST)
    policies = manifest.get("policies")
    if not isinstance(policies, dict) or not policies:
        raise ContextError("MISSING_MACHINE_POLICIES")
    negative_binding = manifest.get("negative_assertions")
    if not isinstance(negative_binding, dict) or negative_binding.get("active") is not True:
        raise ContextError("MISSING_ACTIVE_NEGATIVE_ASSERTIONS_BINDING")
    current_bindings = [*policies.values(), negative_binding]
    forbidden = []
    for binding in current_bindings:
        path = safe_path(binding["path"])
        if binding.get("active") is True:
            actual = snapshot.read(path)[1]
            if not re.fullmatch(r"[0-9a-f]{64}", binding.get("sha256", "")) or actual["sha256"] != binding["sha256"]:
                raise ContextError(f"ACTIVE_POLICY_HASH_MISMATCH: {path}")
            mandatory.add(path)
        else:
            forbidden.append({"path": path, "reason": "INACTIVE_POLICY_NOT_CURRENT_AUTHORITY"})
    forbidden_paths = {x["path"] for x in forbidden}
    if (mandatory | optional) & forbidden_paths:
        raise ContextError("CURRENT_STALE_CONTEXT_CONTRADICTION")
    # 候選 specification 可變；operational authority pointers 必須維持施工 baseline 的 exact bytes。
    for path in set(policy["required"]) | {MASTER_MANIFEST} | {
        binding["path"] for binding in current_bindings if binding.get("active") is True
    }:
        if snapshot.read(path)[1]["git_blob"] != source.read(path)[1]["git_blob"]:
            raise ContextError(f"OPERATIONAL_SOURCE_BASELINE_DRIFT: {path}")
    if not any(binding.get("active") is True for binding in policies.values()):
        raise ContextError("NO_ACTIVE_MACHINE_POLICY")
    mandatory_refs = [snapshot.read(p)[1] for p in sorted(mandatory)]
    optional_refs = [snapshot.read(p)[1] for p in sorted(optional)]
    normalized = {**request, "changed_paths": paths, "architecture_domains": sorted(domains)}
    output = {"schema_version": "p00.context_manifest.v1", "request": normalized,
        "source_baseline_sha": source_baseline, "resolver_binding": tool_binding,
        "authority": "NONE_CONTEXT_ONLY", "execution_eligible": False,
        "mandatory_context": mandatory_refs, "optional_context": optional_refs,
        "forbidden_stale_context": sorted({x["path"]: x for x in forbidden}.values(), key=lambda x: x["path"]),
        "evidence_refs": mandatory_refs + optional_refs,
        "limitations": ["Does not resolve current execution authorization or semantic conflicts.",
            "Caller must verify authoritative master drift; a valid context hash is not approval.",
            "Loaded resolver source matches snapshot; independent review and process attestation are not asserted.",
            "Legacy CURRENT histories remain in source until reviewed compact-projection migration."]}
    mandatory_bytes = sum(item["size_bytes"] for item in mandatory_refs)
    output["context_budget"] = {"mandatory_bytes": mandatory_bytes, "target_max_bytes": 131072,
        "status": "WITHIN_TARGET" if mandatory_bytes <= 131072 else "OVER_TARGET_REQUIRES_COMPACTION",
        "truncation_performed": False}
    output["context_hash"] = hashlib.sha256(canonical(output)).hexdigest()
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--changed", nargs="*", default=[])
    parser.add_argument("--domains", nargs="*", default=[])
    args = parser.parse_args()
    result = resolve(args.root, {"task_type": args.task, "package_id": args.package,
        "changed_paths": args.changed, "architecture_domains": args.domains, "baseline_sha": args.baseline})
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
