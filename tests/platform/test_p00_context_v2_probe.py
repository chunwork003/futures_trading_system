"""Context V2 的安全反例；不把 exact projection 當閱讀／語意／runtime qualification。"""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import pytest
import yaml
from scripts.p00_context import canonical, Snapshot
from scripts.p00_context_pack import expand_json
from scripts.p00_context_v2_probe import build_graph, capsule, omission_oracle, sha
from scripts.p00_reading_obligations import RULES

ROOT = Path(__file__).resolve().parents[2]
BASELINE = "6b717d5b7b9447272e5ff35b7715ad33ad6fb026"
PROFILE = "CONTRACT_REVIEW_NO_EFFECTS"

@pytest.fixture(scope="module")
def bound_capsule(tmp_path_factory):
    # SOURCE01 已 exact 授權整合；新版 loaded resolver 不可冒充舊6b snapshot。
    # 使用隔離 Git fixture，保留349已審查來源，僅套用本輪批准的 tool/API bytes。
    root = tmp_path_factory.mktemp("context-v2-source01-integration")
    source = Snapshot(ROOT, "34925695b83b4bc6e38af800ab5044079d37be7f")
    policy = source.read_json("automation/platform/context_policy.v1.json")
    paths = set(policy["required"])
    for package in policy["packages"].values():
        paths.update([package["package_path"], *package["mandatory"], *package["optional"]])
    for items in [*policy["domains"].values(), *policy["role_context"].values()]:
        paths.update(items)
    manifest = source.read_json("automation/governance/master_manifest.v1.yaml")
    paths.update(b["path"] for b in manifest["policies"].values() if b.get("active") is True)
    paths.add(manifest["negative_assertions"]["path"])
    paths.update(rule[3] for rule in RULES)
    paths.update(["automation/platform/context_policy.v1.json", "scripts/p00_context.py"])
    for path in sorted(paths):
        raw = source.read(path)[0]
        if path in {"scripts/p00_context.py", "docs/architecture/V1_API_ARCHITECTURE.md"}:
            raw = (ROOT / path).read_bytes().replace(b"\r\n", b"\n")
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args]).decode().strip()
    git("init", "-q")
    git("config", "user.name", "Fixture")
    git("config", "user.email", "fixture@example.invalid")
    git("config", "core.autocrlf", "false")
    # 只讀取得原 ancestry；fixture commit 為349的後代，保留policy source_baseline。
    git("fetch", "--quiet", "--no-tags", str(ROOT), source.baseline)
    git("update-ref", "HEAD", source.baseline)
    git("read-tree", source.baseline)
    git("add", *sorted(paths))
    git("commit", "-qm", "isolated SOURCE01 exact integration fixture")
    baseline = git("rev-parse", "HEAD")
    graph = build_graph(root, baseline, "P02")
    return root, baseline, capsule(graph, "P02.IMPORT", root, PROFILE)

def test_complete_negative_source_and_references_survive_read_only_stage(bound_capsule):
    root, baseline, bound_capsule = bound_capsule
    docs = bound_capsule["documents"]
    negative = next(n for n in docs if n["id"].endswith("negative_assertions.v2.yaml"))
    value = yaml.safe_load(negative["value"])
    assert len(value["semantics"]["denied"]) == 13
    assert len(value["invariants"]) == 7
    assert len(bound_capsule["negative_ids"]) == 20
    assert bound_capsule["deferred_preflight_sources"]
    for owner in ["python", "bff"]:
        n = next(n for n in docs if n["id"] == "API:" + owner)
        projected = expand_json(n["value"], bound_capsule["schema_pool"])
        original = json.loads((root / n["source"]["path"]).read_text(encoding="utf-8"))
        assert projected["security"] == original["security"]
        assert projected["components"]["securitySchemes"] == original["components"]["securitySchemes"]
        for p in n["selector"]["paths"]:
            assert projected["paths"][p] == original["paths"][p]
        for name, schema in projected["components"]["schemas"].items():
            assert schema == original["components"]["schemas"][name]
    assert bound_capsule["execution_eligible"] is False
    assert bound_capsule["authority"] == "NONE"

@pytest.mark.parametrize("defect", ["negative", "security", "error", "reference", "stale", "scope", "authority"])
def test_source_derived_oracle_rejects_rehashed_adverse_capsule(bound_capsule, defect):
    root, baseline, bound_capsule = bound_capsule
    supplied = deepcopy(bound_capsule)
    if defect == "negative":
        n = next(n for n in supplied["documents"] if n["id"].endswith("negative_assertions.v2.yaml"))
        n["value"] = n["value"].replace("  - CONSUMED_REDISPATCH\n", "")
    elif defect in {"security", "error", "reference"}:
        n = next(n for n in supplied["documents"] if n["id"] == "API:bff")
        if defect == "security":
            n["value"]["value"]["security"] = []
        elif defect == "error":
            operation = n["value"]["value"]["paths"]["/api/v1/dataset-imports"]["post"]
            operation["responses"].pop("401")
        else:
            supplied["schema_pool"].pop(next(iter(supplied["schema_pool"])))
    elif defect == "stale":
        supplied["baseline"] = "0" * 40
    elif defect == "scope":
        supplied["changed_paths"].append("trading/execution.py")
    else:
        supplied["authority"] = "ACCEPTED"
        supplied["execution_eligible"] = True
    for n in supplied["documents"]:
        n["value_sha256"] = sha(canonical(n["value"]))
    with pytest.raises(ValueError, match="OMISSION_STALE_SCOPE_OR_SOURCE_DRIFT"):
        omission_oracle(root, baseline, "P02", "P02.IMPORT", supplied, profile=PROFILE)

def test_stop_wins_even_for_exact_previous_capsule(bound_capsule):
    root, baseline, bound_capsule = bound_capsule
    with pytest.raises(ValueError, match="STOP_REQUIRES_REENTRY"):
        omission_oracle(root, baseline, "P02", "P02.IMPORT", bound_capsule, stop=True, profile=PROFILE)

def test_cross_owner_scope_requires_an_explicit_stage():
    with pytest.raises(ValueError, match="CROSS_PACKAGE"):
        capsule({"package": "P01"}, "P02.IMPORT", ROOT, PROFILE)
    with pytest.raises(ValueError, match="UNKNOWN_STAGE_PROFILE"):
        capsule({"package": "P01"}, "P01.CSV", ROOT, "READY_FOR_EXECUTION")

def test_exact_projection_is_still_not_a_reading_qualification(bound_capsule):
    root, baseline, bound_capsule = bound_capsule
    result = omission_oracle(root, baseline, "P02", "P02.IMPORT", bound_capsule, profile=PROFILE)
    assert result == "EXACT_PROJECTION_ONLY_SEMANTIC_REVIEW_AND_INJECTION_NOT_ASSERTED"
