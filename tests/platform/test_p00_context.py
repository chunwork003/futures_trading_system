"""以隔離 Git fixture 驗證 context evidence，避免 worktree/CRLF 成為 authority。"""

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE_SPEC = importlib.util.spec_from_file_location("p00_context", ROOT / "scripts/p00_context.py")
context = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(context)


def git(root, *args, input=None):
    return subprocess.check_output(["git", "-C", str(root), *args], input=input).decode().strip()


def write(root, path, value):
    destination = root / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(value) if isinstance(value, dict) else value, encoding="utf-8")


def commit(root):
    git(root, "add", ".")
    git(root, "commit", "-qm", "fixture")
    return git(root, "rev-parse", "HEAD")


@pytest.fixture
def repository(tmp_path):
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    git(tmp_path, "config", "user.name", "Fixture")
    git(tmp_path, "config", "core.autocrlf", "false")
    policy = json.loads((ROOT / context.POLICY).read_text(encoding="utf-8"))
    policy.pop("source_baseline_sha", None)
    paths = set(policy["required"])
    for package in policy["packages"].values():
        paths.update([package["package_path"], *package["mandatory"], *package["optional"]])
    for items in [*policy["domains"].values(), *policy["role_context"].values()]:
        paths.update(items)
    for path in paths:
        write(tmp_path, path, "fixture\n")
    write(tmp_path, context.POLICY, policy)
    write(tmp_path, context.RESOLVER_PATH, (ROOT / context.RESOLVER_PATH).read_text(encoding="utf-8"))
    write(tmp_path, "scripts/p00_compile.py", (ROOT / "scripts/p00_compile.py").read_text(encoding="utf-8"))
    write(tmp_path, "automation/platform/package.schema.v1.json",
          json.loads((ROOT / "automation/platform/package.schema.v1.json").read_text(encoding="utf-8")))
    active = "automation/policies/fixture_active.json"
    write(tmp_path, active, "{\"active\":true}\n")
    expected = hashlib.sha256((tmp_path / active).read_bytes()).hexdigest()
    write(tmp_path, context.MASTER_MANIFEST, {"policies": {
        "active": {"path": active, "active": True, "sha256": expected},
        "old": {"path": "automation/policies/fixture_old.json", "active": False}}})
    baseline = commit(tmp_path)
    request = {"task_type": "ARCHITECT", "package_id": "P00", "changed_paths": ["docs/architecture/new.md"],
               "architecture_domains": [], "baseline_sha": baseline}
    return tmp_path, request


def test_same_snapshot_deterministic_and_dirty_worktree_not_authority(repository):
    root, request = repository
    initial = context.resolve(root, request)
    write(root, "docs/CURRENT_STATE.md", "dirty replacement claiming authority")
    write(root, "automation/policies/fixture_active.json", "dirty revoked")
    again = context.resolve(root, request)
    assert again == initial
    assert again["authority"] == "NONE_CONTEXT_ONLY"
    assert again["execution_eligible"] is False
    assert {"product", "api"} <= set(again["request"]["architecture_domains"])
    assert any(x["path"].endswith("fixture_old.json") for x in again["forbidden_stale_context"])
    assert not any(x["path"].endswith("fixture_old.json") for x in again["evidence_refs"])


@pytest.mark.parametrize("path", ["../secrets.txt", "docs/../secrets.txt", "C:/secret", "/etc/passwd", "docs\\x.md",
    "data/sample.csv", ".env", "docs/.env.production", "docs/.git/config", "docs/*", "docs/x\n.md", "docs//x", "--help"])
def test_unsafe_changed_paths_rejected_before_context_selection(repository, path):
    root, request = repository
    request["changed_paths"] = [path]
    with pytest.raises(context.ContextError):
        context.resolve(root, request)


@pytest.mark.parametrize("field,value", [("baseline_sha", "HEAD"), ("baseline_sha", "a" * 39),
    ("package_id", "P99"), ("task_type", "DISPATCH"), ("architecture_domains", ["missing"]),
    ("changed_paths", ["trading/execution.py"]), ("changed_paths", "docs/test.md")])
def test_unregistered_or_unbound_request_fails_closed(repository, field, value):
    root, request = repository
    request[field] = value
    with pytest.raises(context.ContextError):
        context.resolve(root, request)


def test_active_policy_hash_mismatch_is_not_silently_rebound(repository):
    root, request = repository
    write(root, "automation/policies/fixture_active.json", "changed policy")
    request["baseline_sha"] = commit(root)
    with pytest.raises(context.ContextError, match="ACTIVE_POLICY_HASH_MISMATCH"):
        context.resolve(root, request)


def test_required_file_missing_does_not_fallback_to_local_copy(repository):
    root, request = repository
    (root / "docs/CURRENT_STATE.md").unlink()
    request["baseline_sha"] = commit(root)
    write(root, "docs/CURRENT_STATE.md", "untracked fallback")
    with pytest.raises(context.ContextError, match="MISSING_EXACT_FILE"):
        context.resolve(root, request)


def test_git_symlink_is_not_read_as_context(repository):
    root, request = repository
    blob = git(root, "hash-object", "-w", "--stdin", input=b"../../../secrets.txt")
    git(root, "update-index", "--cacheinfo", f"120000,{blob},docs/CURRENT_STATE.md")
    git(root, "commit", "-qm", "symlink fixture")
    request["baseline_sha"] = git(root, "rev-parse", "HEAD")
    with pytest.raises(context.ContextError, match="NON_REGULAR_CONTEXT_FILE"):
        context.resolve(root, request)


def test_changed_path_order_and_duplicates_do_not_change_hash(repository):
    root, request = repository
    request["changed_paths"] = ["docs/architecture/new.md", "docs/program/new.md"]
    first = context.resolve(root, request)
    request["changed_paths"].reverse()
    request["changed_paths"].append("docs/architecture/new.md")
    assert context.resolve(root, request)["context_hash"] == first["context_hash"]


def test_new_committed_source_changes_hash(repository):
    root, request = repository
    first = context.resolve(root, request)
    write(root, "docs/architecture/V1_CONTRACTS.md", "new semantics")
    request["baseline_sha"] = commit(root)
    second = context.resolve(root, request)
    assert first["context_hash"] != second["context_hash"]


def test_stale_policy_in_mandatory_set_is_contradiction(repository):
    root, request = repository
    policy = json.loads((root / context.POLICY).read_text(encoding="utf-8"))
    policy["required"].append("automation/policies/fixture_old.json")
    write(root, context.POLICY, policy)
    request["baseline_sha"] = commit(root)
    with pytest.raises(context.ContextError, match="CURRENT_STALE_CONTEXT_CONTRADICTION"):
        context.resolve(root, request)


def test_large_context_is_reported_without_silent_truncation(repository):
    root, request = repository
    write(root, "docs/CURRENT_STATE.md", "x" * 150000)
    request["baseline_sha"] = commit(root)
    result = context.resolve(root, request)
    assert result["context_budget"]["status"] == "OVER_TARGET_REQUIRES_COMPACTION"
    assert result["context_budget"]["truncation_performed"] is False
    assert result["execution_eligible"] is False
    current = next(x for x in result["mandatory_context"] if x["path"] == "docs/CURRENT_STATE.md")
    assert current["size_bytes"] == 150000


def test_different_loaded_resolver_is_rejected(repository):
    root, request = repository
    path = root / context.RESOLVER_PATH
    path.write_text(path.read_text(encoding="utf-8") + "\n# changed tool\n", encoding="utf-8")
    request["baseline_sha"] = commit(root)
    with pytest.raises(context.ContextError, match="LOADED_TOOL_SOURCE_MISMATCH"):
        context.resolve(root, request)


def test_distinct_source_baseline_rejects_operational_drift(repository):
    root, request = repository
    policy = json.loads((root / context.POLICY).read_text(encoding="utf-8"))
    policy["source_baseline_sha"] = request["baseline_sha"]
    write(root, context.POLICY, policy)
    request["baseline_sha"] = commit(root)
    assert context.resolve(root, request)["source_baseline_sha"] == policy["source_baseline_sha"]
    write(root, "docs/CURRENT_STATE.md", "unaccepted operational change")
    request["baseline_sha"] = commit(root)
    with pytest.raises(context.ContextError, match="OPERATIONAL_SOURCE_BASELINE_DRIFT"):
        context.resolve(root, request)


def test_bound_compiler_rehydrates_even_if_attacker_rehashes_context(repository):
    from scripts.p00_compile import compile_bound
    from test_p00_compiler import inputs
    root, request = repository
    manifest = context.resolve(root, request)
    package, _ = inputs()
    package["identity"]["baseline_sha"] = request["baseline_sha"]
    package["authority"]["exact_scope"] = request["changed_paths"]
    package["design"]["input_output_schemas"] = ["automation/platform/package.schema.v1.json"]
    result = compile_bound(root, package, manifest)
    assert result["provenance_validation"] == "SNAPSHOT_AND_LOADED_SOURCE_MATCH_REVIEW_NOT_ASSERTED"
    assert result["execution_eligible"] is False
    manifest["context_budget"]["mandatory_bytes"] += 1
    manifest["context_hash"] = hashlib.sha256(context.canonical({k: v for k, v in manifest.items() if k != "context_hash"})).hexdigest()
    with pytest.raises(ValueError, match="CONTEXT_REHYDRATION_MISMATCH"):
        compile_bound(root, package, manifest)
