"""唯讀重建 SOURCE01 patch 與 hypothetical resolver；不套用、無 receipt／authority。"""
from copy import deepcopy
import ast
import difflib
import hashlib
import json
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from p00_context import Snapshot, canonical, resolve
from p00_context_pack import build_pack
from p00_reading import governance_coverage

INPUT = "52fdbe074e27004e2e4f1dbb2615920ef93e47e5"
MASTER = "9b5ab5fdd98744a7db45ec9f14b64ef1f324920f"
OWNER = "scripts/p00_context.py"
NEGATIVE = "automation/specs/negative_assertions.v2.yaml"
PREFIX = "docs/program/decisions/R06-SOURCE-01"


def amendment(raw):
    text = raw.decode("utf-8")
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
    new = '        binding["path"] for binding in current_bindings if binding.get("active") is True'
    assert text.count(old) == 1
    text = text.replace(old, new)
    ast.parse(text)
    proposed = text.encode("utf-8")
    patch = "".join(difflib.unified_diff(raw.decode().splitlines(True), text.splitlines(True),
        fromfile="a/" + OWNER, tofile="b/" + OWNER, n=0)).encode("utf-8")
    return proposed, patch


def reproduce():
    s = Snapshot(ROOT, INPUT)
    raw, before = s.read(OWNER)
    proposed, patch = amendment(raw)
    assert (ROOT / (PREFIX + ".resolver-candidate.patch")).read_bytes() == patch
    negative = yaml.safe_load(s.read(NEGATIVE)[0])
    policy = s.read_json("automation/platform/context_policy.v1.json")
    manifest = s.read_json("automation/governance/master_manifest.v1.yaml")
    source_refs = governance_coverage(s, {"mandatory_context": []})["declared_source_refs"]
    assert len(source_refs) == 7
    h = lambda b: hashlib.sha256(b).hexdigest()
    # 此 overlay 只作候選流程推演，沒有對應 Git commit；不能作 trusted source/receipt。
    overlays = {}
    class HypotheticalSnapshot(Snapshot):
        def read(self, path):
            if self.baseline == INPUT and path in overlays:
                value = overlays[path]
                ref = {"path": path, "baseline_sha": self.baseline,
                    "git_blob": hashlib.sha1(b"blob " + str(len(value)).encode() + b"\0" + value).hexdigest(),
                    "sha256": h(value), "size_bytes": len(value)}
                return value, ref
            return super().read(path)
    env = {"__name__": "source01_hypothetical_only", "__file__": str(ROOT / OWNER)}
    exec(compile(proposed, "<SOURCE01-CANDIDATE-IN-MEMORY>", "exec"), env)
    env["Snapshot"] = HypotheticalSnapshot
    env["bind_loaded_source"] = lambda snapshot, path, loaded: {
        **snapshot.read(path)[1], "source_comparison": "HYPOTHETICAL_PATCH_NOT_GIT_OR_PROCESS_BINDING",
        "review_status": "NOT_ASSERTED"}
    results = []
    candidate_contexts = {}
    overlays[OWNER] = proposed
    for package in ("P01", "P02"):
        request = {"task_type": "WORK", "package_id": package,
            "changed_paths": s.read_json("docs/program/packages/" + package + ".candidate.v1.json")["authority"]["exact_scope"],
            "architecture_domains": ["program"], "baseline_sha": INPUT}
        original = resolve(ROOT, request)
        hypothetical = env["resolve"](ROOT, request)
        old_paths = {x["path"] for x in original["mandatory_context"]}
        new_paths = {x["path"] for x in hypothetical["mandatory_context"]}
        assert new_paths == old_paths | {NEGATIVE}
        assert all(x["path"] in new_paths for x in source_refs)
        assert hypothetical["execution_eligible"] is False
        assert hypothetical["authority"] == "NONE_CONTEXT_ONLY"
        assert hypothetical["context_budget"]["target_max_bytes"] == 131072
        assert hypothetical["context_budget"]["mandatory_bytes"] == original["context_budget"]["mandatory_bytes"] + len(s.read(NEGATIVE)[0]) + len(proposed) - len(raw)
        assert s.read(NEGATIVE)[0] == Snapshot(ROOT, MASTER).read(NEGATIVE)[0]
        _, metrics = build_pack(ROOT, request, selective=True)
        candidate_contexts[package] = request
        results.append({"package": package, "original_mandatory_bytes": original["context_budget"]["mandatory_bytes"],
            "existing_selective_pack_bytes": metrics["reading_pack_bytes"],
            "hypothetical_corrected_mandatory_bytes": hypothetical["context_budget"]["mandatory_bytes"],
            "source_set_delta": [NEGATIVE], "original_gate": "NOT_PASSED", "hypothetical_gate": "NOT_PASSED",
            "hypothetical_is_not_committed_context": True,
            "top_sources": sorted(original["mandatory_context"], key=lambda r: (-r["size_bytes"], r["path"]))[:12]})
    # 反例只在 memory overlay；原始 accepted sources 完全不寫入。
    cases = []
    for case in ("missing", "inactive", "hash_mismatch", "unsafe_path", "negative_baseline_drift", "inactive_policy_in_required"):
        overlays.clear(); overlays[OWNER] = proposed
        changed = deepcopy(manifest)
        expected = ""
        if case == "missing":
            del changed["negative_assertions"]; expected = "MISSING_ACTIVE_NEGATIVE_ASSERTIONS_BINDING"
        elif case == "inactive":
            changed["negative_assertions"]["active"] = False; expected = "MISSING_ACTIVE_NEGATIVE_ASSERTIONS_BINDING"
        elif case == "hash_mismatch":
            changed["negative_assertions"]["sha256"] = "0" * 64; expected = "ACTIVE_POLICY_HASH_MISMATCH"
        elif case == "unsafe_path":
            changed["negative_assertions"]["path"] = "data/forbidden.yaml"; expected = "FORBIDDEN_REPOSITORY_PATH"
        elif case == "negative_baseline_drift":
            value = s.read(NEGATIVE)[0] + b"# hypothetical drift\n"
            overlays[NEGATIVE] = value; changed["negative_assertions"]["sha256"] = h(value)
            expected = "OPERATIONAL_SOURCE_BASELINE_DRIFT"
        else:
            cp = deepcopy(policy)
            inactive = next(b["path"] for b in manifest["policies"].values() if b.get("active") is not True)
            cp["required"].append(inactive)
            overlays["automation/platform/context_policy.v1.json"] = canonical(cp)
            expected = "CURRENT_STALE_CONTEXT_CONTRADICTION"
        overlays["automation/governance/master_manifest.v1.yaml"] = canonical(changed)
        try:
            env["resolve"](ROOT, candidate_contexts["P01"])
            raise AssertionError("ADVERSE_NOT_REJECTED: " + case)
        except env["ContextError"] as error:
            assert str(error).startswith(expected), (case, str(error), expected)
            cases.append({"case": case, "outcome": expected, "scope": "IN_MEMORY_NOT_BACKEND_OR_MODEL_QUALIFICATION"})
    overlays.clear()
    current_pair = [s.read(p)[1] for p in ("docs/CURRENT_STATE.md", "docs/CURRENT_WORK.md")]
    return {"schema_version": "p00.source01_reproduction.v1", "input": INPUT, "source_master": MASTER,
        "before_owner": before, "proposed_raw_sha256": h(proposed), "proposed_size_bytes": len(proposed),
        "owner_size_delta": len(proposed) - len(raw), "patch_sha256": h(patch),
        "declared_active_refs": source_refs, "negative_denied": negative["semantics"]["denied"],
        "negative_invariants": negative["invariants"], "packages": results, "adverses": cases,
        "current_pair": current_pair, "current_pair_bytes": sum(x["size_bytes"] for x in current_pair),
        "checks": "EXACT_PATCH_AST_PATH_SET_HASH_DRIFT_NONAUTHORITY_PASS_HYPOTHETICAL_ONLY",
        "applied": False, "trusted_receipts_created": False, "semantic_review": "NOT_PERFORMED"}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(reproduce(), ensure_ascii=False, indent=2))
