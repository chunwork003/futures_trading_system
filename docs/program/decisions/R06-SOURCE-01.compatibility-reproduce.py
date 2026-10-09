"""隔離 SOURCE01 五檔候選；只寫 ignored fixture，不套用原 repo、不建立 operational evidence。"""
import argparse
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from p00_context import Snapshot, canonical, resolve
INPUT = "bae9dcaff476bd79e8494ac6cd393dea19cb9657"
PREFIX = "docs/program/decisions/R06-SOURCE-01"
OWNER = "scripts/p00_context.py"


def candidates():
    s = Snapshot(ROOT, INPUT)
    paths = [OWNER, "scripts/p00_reading_eval.py", "tests/platform/test_p00_context.py",
             "tests/platform/test_p00_reading.py", "tests/platform/test_p00_reading_eval.py"]
    before = {path: s.read(path)[0] for path in paths}
    proposed = dict(before)
    # Owner patch 使用已保存原三個 hunks；文字替換僅產生候選 bytes。
    text = before[OWNER].decode()
    old = '    forbidden = []\n    for binding in policies.values():'
    new = '''    negative_binding = manifest.get("negative_assertions")
    if not isinstance(negative_binding, dict) or negative_binding.get("active") is not True:
        raise ContextError("MISSING_ACTIVE_NEGATIVE_ASSERTIONS_BINDING")
    current_bindings = [*policies.values(), negative_binding]
    forbidden = []
    for binding in current_bindings:'''
    assert text.count(old) == 1
    text = text.replace(old, new)
    old = '        binding["path"] for binding in policies.values() if binding.get("active") is True'
    assert text.count(old) == 1
    text = text.replace(old, '        binding["path"] for binding in current_bindings if binding.get("active") is True')
    proposed[OWNER] = text.encode()
    original = s.read_json(PREFIX + ".proposal.v1.json")
    assert hashlib.sha256(proposed[OWNER]).hexdigest() == original["recommended_candidate"]["after_raw_sha256"]
    path = "scripts/p00_reading_eval.py"
    text = before[path].decode()
    start = text.index("    # source01 ")
    stop = text.index('    rows.append({"id":"ORIGINAL_AGGREGATE_BUDGET"', start)
    text = text[:start] + '''    # 原 gap 報告不改寫；successor representation 仍非語意／閱讀／intake qualification。
    negative_path = "automation/specs/negative_assertions.v2.yaml"
    if coverage["status"] == "UNREPRESENTED_DECLARED_GOVERNANCE_SOURCES":
        if not any(r["path"] == negative_path for r in coverage["unrepresented_sources"]):
            raise AssertionError("SOURCE01_EXPECTED_UNRESOLVED_BINDING_CHANGED_REVIEW_REQUIRED")
        rows.append({"id":"ACTIVE_NEGATIVE_SOURCE_GAP", "outcome":"KNOWN_SOURCE_GAP_STILL_OPEN", "missing_sources":coverage["unrepresented_sources"],"semantic_completeness":"NOT_ASSERTED"})
    elif coverage["status"] == "DECLARED_BINDINGS_REPRESENTED_NOT_QUALIFIED":
        declared = {r["path"]: r for r in coverage["declared_source_refs"]}
        mandatory = {r["path"]: r for r in context["mandatory_context"]}
        if (coverage["unrepresented_sources"] or coverage["negative_assertions_binding"] != "SOURCE_HASH_VERIFIED"
                or coverage["semantic_completeness"] != "NOT_ASSERTED" or coverage["current_intake_complete"] is not False
                or negative_path not in declared or any(canonical(r) != canonical(mandatory.get(p)) for p, r in declared.items())):
            raise AssertionError("SOURCE01_REPRESENTATION_CONTRADICTION")
        rows.append({"id":"ACTIVE_NEGATIVE_SOURCE_REPRESENTED_NOT_QUALIFIED", "outcome":"DECLARED_BINDING_REPRESENTED_NOT_SEMANTIC_OR_TRUST_QUALIFICATION", "missing_sources":[],"semantic_completeness":"NOT_ASSERTED"})
    else:
        raise AssertionError("SOURCE01_UNKNOWN_COVERAGE_REVIEW_REQUIRED")
''' + text[stop:]
    proposed[path] = text.encode()
    path = "tests/platform/test_p00_context.py"
    text = before[path].decode()
    old = '    write(tmp_path, context.MASTER_MANIFEST, {"policies": {'
    new = '''    negative = "automation/specs/negative_assertions.fixture.json"
    write(tmp_path, negative, "deny")
    write(tmp_path, context.MASTER_MANIFEST, {"negative_assertions": {
        "path": negative, "active": True, "sha256": hashlib.sha256(b"deny").hexdigest()}, "policies": {'''
    assert text.count(old) == 1
    text = text.replace(old, new)
    text += '''

@pytest.mark.parametrize("change,reason", [
    ("missing", "MISSING_ACTIVE_NEGATIVE_ASSERTIONS_BINDING"),
    ("inactive", "MISSING_ACTIVE_NEGATIVE_ASSERTIONS_BINDING"),
    ("hash", "ACTIVE_POLICY_HASH_MISMATCH"),
    ("unsafe", "FORBIDDEN_REPOSITORY_PATH")])
def test_negative_binding_missing_inactive_hash_or_unsafe_fails_closed(repository, change, reason):
    root, request = repository
    manifest = json.loads((root / context.MASTER_MANIFEST).read_text(encoding="utf-8"))
    if change == "missing": del manifest["negative_assertions"]
    if change == "inactive": manifest["negative_assertions"]["active"] = False
    if change == "hash": manifest["negative_assertions"]["sha256"] = "0" * 64
    if change == "unsafe": manifest["negative_assertions"]["path"] = "data/forbidden.json"
    write(root, context.MASTER_MANIFEST, manifest)
    request["baseline_sha"] = commit(root)
    with pytest.raises(context.ContextError, match=reason): context.resolve(root, request)


def test_negative_required_once_even_if_manifest_alias_and_dirty_worktree(repository):
    root, request = repository
    manifest = json.loads((root / context.MASTER_MANIFEST).read_text(encoding="utf-8"))
    negative = manifest["negative_assertions"]
    manifest["policies"]["negative_alias"] = deepcopy(negative)
    write(root, context.MASTER_MANIFEST, manifest)
    request["baseline_sha"] = commit(root)
    result = context.resolve(root, request)
    assert sum(x["path"] == negative["path"] for x in result["mandatory_context"]) == 1
    write(root, negative["path"], "dirty contradictory override")
    assert context.resolve(root, request) == result
    assert result["execution_eligible"] is False


def test_negative_valid_hash_drift_still_rejected_against_source_baseline(repository):
    root, request = repository
    policy = json.loads((root / context.POLICY).read_text(encoding="utf-8"))
    policy["source_baseline_sha"] = request["baseline_sha"]
    write(root, context.POLICY, policy)
    request["baseline_sha"] = commit(root)
    manifest = json.loads((root / context.MASTER_MANIFEST).read_text(encoding="utf-8"))
    value = "changed negative policy"
    write(root, manifest["negative_assertions"]["path"], value)
    manifest["negative_assertions"]["sha256"] = hashlib.sha256(value.encode()).hexdigest()
    write(root, context.MASTER_MANIFEST, manifest)
    request["baseline_sha"] = commit(root)
    with pytest.raises(context.ContextError, match="OPERATIONAL_SOURCE_BASELINE_DRIFT"):
        context.resolve(root, request)
'''
    proposed[path] = text.encode()
    path = "tests/platform/test_p00_reading.py"
    text = before[path].decode()
    old = '    assert plan["governance_source_coverage"]["status"] == "UNREPRESENTED_DECLARED_GOVERNANCE_SOURCES"\n    assert plan["governance_source_coverage"]["unrepresented_sources"][0]["path"] == negative_path'
    new = '''    assert plan["governance_source_coverage"]["status"] == "DECLARED_BINDINGS_REPRESENTED_NOT_QUALIFIED"
    assert plan["governance_source_coverage"]["unrepresented_sources"] == []
    assert any(o["source"]["path"] == negative_path for o in plan["obligations"])
    assert plan["governance_source_coverage"]["semantic_completeness"] == "NOT_ASSERTED"
    assert first["audit"]["actual_reading_verified"] is False
    assert first["audit"]["current_intake_complete"] is False'''
    assert text.count(old) == 1
    proposed[path] = text.replace(old, new).encode()
    path = "tests/platform/test_p00_reading_eval.py"
    text = before[path].decode().replace("import hashlib\n", "import hashlib\nimport subprocess\nfrom copy import deepcopy\n")
    text = text.replace('BASE="36f6c0779227ea9a735d3650cad1d98ee8a2f19c"', 'HISTORICAL_BASE="36f6c0779227ea9a735d3650cad1d98ee8a2f19c"\n# 測試先固定完整fixture/current HEAD；不使用HEAD作runtime execution authority。\nBASE=subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"]).decode().strip()')
    old = '    missing=cases["ACTIVE_NEGATIVE_SOURCE_GAP"]["missing_sources"]\n    assert any(s["path"]=="automation/specs/negative_assertions.v2.yaml" for s in missing)'
    new = '''    represented=cases["ACTIVE_NEGATIVE_SOURCE_REPRESENTED_NOT_QUALIFIED"]
    assert represented["missing_sources"] == []
    assert represented["semantic_completeness"] == "NOT_ASSERTED"
    assert represented["outcome"] == "DECLARED_BINDING_REPRESENTED_NOT_SEMANTIC_OR_TRUST_QUALIFICATION"'''
    assert text.count(old) == 1
    text = text.replace(old, new)
    text += '''


def test_historical_source_owner_cannot_be_silently_rebound_to_successor():
    snap = Snapshot(ROOT, HISTORICAL_BASE)
    req = {"task_type":"WORK", "package_id":"P01", "changed_paths":snap.read_json("docs/program/packages/P01.candidate.v1.json")["authority"]["exact_scope"], "architecture_domains":["program"], "baseline_sha":HISTORICAL_BASE}
    from scripts.p00_context import ContextError
    with pytest.raises(ContextError, match="LOADED_TOOL_SOURCE_MISMATCH"):
        resolve(ROOT, req)


@pytest.mark.parametrize("change", ["unknown", "missing", "hash", "semantics", "intake"])
def test_represented_source_coverage_contradictions_do_not_qualify(evaluation, change):
    context, pack, consumer, schema, coverage = evaluation
    altered = deepcopy(coverage)
    if change == "unknown": altered["status"] = "NEGATIVE_ASSERTIONS_BINDING_UNKNOWN"
    if change == "missing": altered["unrepresented_sources"] = [altered["declared_source_refs"][0]]
    if change == "hash": altered["declared_source_refs"][0]["sha256"] = "0" * 64
    if change == "semantics": altered["semantic_completeness"] = "QUALIFIED"
    if change == "intake": altered["current_intake_complete"] = True
    with pytest.raises(AssertionError, match="SOURCE01_"):
        exercise(context, pack, consumer, schema, altered)
'''
    proposed[path] = text.encode()
    for value in proposed.values(): ast.parse(value)
    patch = b"".join("".join(difflib.unified_diff(before[path].decode().splitlines(True), proposed[path].decode().splitlines(True), fromfile="a/"+path, tofile="b/"+path, n=0)).encode() for path in paths)
    return s, before, proposed, patch


def isolated(fixture):
    fixture = fixture.resolve()
    assert fixture.is_relative_to((ROOT / ".tmp").resolve()) and not fixture.exists()
    fixture.mkdir(parents=True)
    (fixture / ".tmp").mkdir()
    s, before, proposed, patch = candidates()
    original_worktree_head = s.git("rev-parse", "HEAD").decode().strip()
    assert (ROOT / (PREFIX + ".compatibility-candidate.patch")).read_bytes() == patch
    git = lambda *args, **kw: subprocess.check_output(["git", "-C", str(fixture), *args], **kw)
    git("init", "-q"); git("config", "core.autocrlf", "false")
    objects = Path(s.git("rev-parse", "--git-path", "objects").decode().strip())
    if not objects.is_absolute(): objects = ROOT / objects
    assert objects.is_dir()
    (fixture / ".git/objects/info/alternates").write_bytes((objects.resolve().as_posix()+"\n").encode("utf-8"))
    # 只在隔離 index 保留原tree與parent；不checkout/讀取產品或data內容。
    git("read-tree", INPUT)
    source_paths = {"automation/platform/context_policy.v1.json", "automation/platform/context_selection.v1.json",
        "automation/platform/reading_claim.schema.v1.json", "automation/platform/context_reading_contract.v1.json",
        "automation/platform/package.schema.v1.json", "scripts/p00_context_pack.py", "scripts/p00_reading.py",
        "scripts/p00_compile.py", "tests/platform/test_p00_context_pack.py", "tests/platform/test_p00_compiler.py"}
    policy = s.read_json("automation/platform/context_policy.v1.json")
    source_paths.update(policy["required"])
    for package in policy["packages"].values(): source_paths.update([package["package_path"],*package["mandatory"],*package["optional"]])
    for paths in [*policy["domains"].values(),*policy["role_context"].values()]: source_paths.update(paths)
    for path in sorted(source_paths | proposed.keys()):
        dest = fixture / path; dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(proposed.get(path, s.read(path)[0]))
    git("add", "--", *sorted(proposed))
    tree = git("write-tree").decode().strip()
    env = {**os.environ, "GIT_AUTHOR_NAME":"P00 isolated fixture", "GIT_COMMITTER_NAME":"P00 isolated fixture",
        "GIT_AUTHOR_EMAIL":"fixture@example.invalid", "GIT_COMMITTER_EMAIL":"fixture@example.invalid",
        "GIT_AUTHOR_DATE":"2026-10-09T22:25:27+00:00", "GIT_COMMITTER_DATE":"2026-10-09T22:25:27+00:00"}
    sha = git("commit-tree", tree, "-p", INPUT, "-m", "SOURCE01 isolated hypothetical compatibility fixture - no authority", env=env).decode().strip()
    git("update-ref", "refs/heads/master", sha)
    assert s.git("rev-parse", "HEAD").decode().strip() == original_worktree_head
    report = {"status":"ISOLATED_SYNTHETIC_GIT_FIXTURE_NOT_OPERATIONAL_MIGRATION", "input":INPUT,
        "fixture_commit":sha, "fixture":str(fixture), "patch_sha256":hashlib.sha256(patch).hexdigest(),
        "patched_files":[{"path":path,"before":s.read(path)[1],"after_sha256":hashlib.sha256(raw).hexdigest(),"after_size_bytes":len(raw)} for path,raw in proposed.items()],
        "original_refs_unchanged":True,"operational_evidence_created":False,"acceptance":False,
        "pytest_command":"python -B -m pytest tests/platform/test_p00_context.py tests/platform/test_p00_compiler.py tests/platform/test_p00_context_pack.py tests/platform/test_p00_reading.py tests/platform/test_p00_reading_eval.py -q -p no:cacheprovider --basetemp .tmp/test-temp"}
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--fixture", required=True)
    args = parser.parse_args(); sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(isolated(Path(args.fixture)),ensure_ascii=False,indent=2))
