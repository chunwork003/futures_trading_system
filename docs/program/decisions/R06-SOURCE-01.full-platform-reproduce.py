"""擴充既有五檔隔離候選至完整 platform；不套用原 repository、不重綁歷史證據。"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
RECIPE = ROOT / "docs/program/decisions/R06-SOURCE-01.compatibility-reproduce.py"
INPUT = "bae9dcaff476bd79e8494ac6cd393dea19cb9657"

def materialize(fixture):
    spec = importlib.util.spec_from_file_location("source01_candidate_recipe", RECIPE)
    recipe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recipe)
    report = recipe.isolated(fixture)
    s = recipe.Snapshot(ROOT, INPUT)
    # 只列舉明確 P00 families；不 checkout 產品、accepted engine 或 data。
    paths = s.git("ls-tree", "-r", "--name-only", INPUT, "--",
        "automation/platform", "docs/architecture", "docs/program", "tests/platform", "scripts").decode().splitlines()
    paths = sorted(p for p in paths if not p.startswith("scripts/") or p.startswith("scripts/p00_"))
    # 既有 platform 的唯讀產品相容測試依賴；來源完全不變，沒有產品實作。
    runtime_paths = ["domain/market_observation.py", "pyproject.toml"]
    runtime_paths += ["features/" + name + ".py" for name in ["__init__", "builder", "momentum", "price", "registry", "rolling", "technical", "trend", "volatility"]]
    runtime_paths += ["backtest/" + name + ".py" for name in ["__init__", "models", "risk", "strategy_priority_policy", "strategy_conflict_policy", "strategy_position"]]
    paths = sorted(set(paths + runtime_paths))
    proposed = {row["path"]: row for row in report["patched_files"]}
    refs = []
    for path in paths:
        if path in proposed:
            assert hashlib.sha256((fixture / path).read_bytes()).hexdigest() == proposed[path]["after_sha256"]
            continue
        raw, ref = s.read(path)
        dest = fixture / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists(): assert dest.read_bytes() == raw
        else: dest.write_bytes(raw)
        refs.append(ref)
    assert recipe.Snapshot(fixture, report["fixture_commit"]).git("diff", "--name-only", INPUT, report["fixture_commit"]).decode().splitlines() == sorted(proposed)
    report.update(schema_version="p00.source01_full_platform_fixture.v1",
        materialized_unchanged_source_refs=refs,
        materialization_rule="EXACT_INPUT_BLOBS_P00_AND_EXISTING_READONLY_COMPATIBILITY_IMPORT_CLOSURE_NO_NEW_TREE_DELTA",
        runtime_import_paths=runtime_paths,
        pytest_command="python -B -m pytest tests/platform -q -p no:cacheprovider --basetemp .tmp/full-platform-temp",
        full_platform_result="NOT_RUN", original_repository_adoption=False,
        model_backend_semantic_qualification=False)
    (fixture / ".tmp/full-platform-materialization.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return report

if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True)
    args=parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    report=materialize(Path(args.fixture).resolve())
    print(json.dumps({k:v for k,v in report.items() if k not in ("materialized_unchanged_source_refs", "patched_files")}, ensure_ascii=False, indent=2))
    print("materialized_unchanged_source_refs",len(report["materialized_unchanged_source_refs"]))
