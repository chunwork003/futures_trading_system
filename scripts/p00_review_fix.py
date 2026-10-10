"""P00 受限修正離線驗證：重建已批准 patch，保留原條款；不授權或宣稱 runtime conformance。"""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
try:
    from p00_context import Snapshot
except ModuleNotFoundError:
    from scripts.p00_context import Snapshot

DECISION = "docs/program/decisions/P00-bounded-correction.v1.json"
CANDIDATE = "docs/program/decisions/P00-bottleneck-resolution.decision.v1.json"
EXPECTED_EXCEPTIONS = {"EX-HIST-UNIVERSE", "EX-R05-MEASURED", "EX-RQ-DESIGN-ORDER"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()



def pointer(value, selector):
    for part in selector.lstrip("/").split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def verify_csv(root, snapshot, decision, report=None, delta=None):
    """核對原 reviewer literal/Q01 source pins 與 successor delta；不執行產品格式解析。"""
    for binding in decision["CSV_EXACT_WORK_PACKAGE"]["source_pins"]:
        raw, actual = snapshot.read(binding["path"])
        if actual["sha256"] != binding["sha256"] or actual["git_blob"] != binding["git_blob"]:
            raise ValueError("CSV_SOURCE_PIN_DRIFT")
        if (root / binding["path"]).read_bytes().replace(b"\r\n", b"\n") != raw.replace(b"\r\n", b"\n"):
            raise ValueError("CSV_PROTECTED_SOURCE_CHANGED")
    if report is None:
        report = json.loads((root / "docs/program/reviews/P00-bottleneck-3492569/csv-review.json").read_text(encoding="utf-8"))
    fixtures = report["fixture_recommendation"]
    for name in ["ten", "nine"]:
        if sha(fixtures[name + "_column_utf8_LF"].encode("utf-8")) != fixtures[name + "_sha256"]:
            raise ValueError("CSV_LITERAL_FIXTURE_DRIFT")
    sources = report["fixture_hash_binding"]["sources"]
    documents = {}
    for path, binding in sources.items():
        raw, actual = snapshot.read(path)
        if actual["sha256"] != binding["raw_sha256"] or actual["git_blob"] != binding["git_blob"] or binding["commit"] != snapshot.baseline:
            raise ValueError("CSV_FIXTURE_SOURCE_DRIFT")
        documents[path] = json.loads(raw)
    checks = report["fixture_hash_binding"]
    for key, path, expected in [
        ("Q01_pointer_bindings", "docs/architecture/contracts/dataset_quality.fixture.v1.json", {"/cases/0/input/calendar", "/cases/0/input/mapping", "/cases/0/input/coverage"}),
        ("dataset_identity_row_bindings", "docs/architecture/contracts/dataset_identity.fixture.v1.json", {"/rows/0", "/rows/1"})]:
        if set(checks[key]) != expected:
            raise ValueError("CSV_FIXTURE_POINTER_OMITTED")
        for selector, binding in checks[key].items():
            value = pointer(documents[path], selector)
            encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"
            if sha(encoded) != binding["value_sha256_compact_sorted_UTF8_LF"]:
                raise ValueError("CSV_FIXTURE_VALUE_DRIFT")
    if delta is None:
        delta = json.loads((root / "automation/platform/source_reading_obligations.csv-a.delta.v1.json").read_text(encoding="utf-8"))
    for key in ["predecessor", "affected_source_before"]:
        actual = snapshot.read(delta[key]["path"])[1]
        if any(delta[key][k] != actual[k] for k in ["git_blob", "sha256", "baseline_sha"]):
            raise ValueError("CSV_DELTA_SOURCE_DRIFT")
    registry = snapshot.read_json(delta["predecessor"]["path"])
    expected_ids = [o["id"] for o in registry["critical_semantic_obligations"] if o["source_path"] in {"docs/architecture/V1_API_ARCHITECTURE.md", "docs/architecture/V1_DATASET_IDENTITY_IO.md"}]
    api = root / "docs/architecture/V1_API_ARCHITECTURE.md"
    if delta["affected_obligation_ids"] != expected_ids or delta["preserved_source_units"] != registry["source_findings"][1]["source_units"]:
        raise ValueError("CSV_DELTA_OBLIGATION_OMITTED")
    if delta["affected_source_after_normalized_lf_sha256"] != sha(api.read_bytes().replace(b"\r\n", b"\n")):
        raise ValueError("CSV_DELTA_AFTER_SOURCE_DRIFT")
    if delta["compiler_gate_changed"] is not False or delta["actual_reading_verified"] is not False or delta["full_source_fallback"] is not True:
        raise ValueError("CSV_DELTA_FALSE_QUALIFICATION")

def verify(root, supplied=None):
    """證明 exact source/patch preservation；Human decision 紀錄不是自動 authority resolver。"""
    root = Path(root)
    decision = deepcopy(supplied) if supplied is not None else json.loads((root / DECISION).read_text(encoding="utf-8"))
    snapshot = Snapshot(root, decision["review_subject"])
    for binding in decision["untouched_original_sources"]:
        expected, actual = snapshot.read(binding["path"])
        if actual["sha256"] != binding["sha256"] or actual["git_blob"] != binding["git_blob"]:
            raise ValueError("ORIGINAL_BINDING_DRIFT")
        if (root / binding["path"]).read_bytes().replace(b"\r\n", b"\n") != expected.replace(b"\r\n", b"\n"):
            raise ValueError("ORIGINAL_AUTHORITY_OR_HISTORY_REWRITTEN")
    predicates = decision["original_acceptance_predicates"]
    if [p["id"] for p in predicates] != [f"P00-AC{i:02d}" for i in range(1, 8)]:
        raise ValueError("ACCEPTANCE_PREDICATE_OMITTED")
    exceptions = decision["closure_exceptions"]
    if {e["exception_id"] for e in exceptions} != EXPECTED_EXCEPTIONS or len(exceptions) != 3:
        raise ValueError("EXCEPTION_INVENTORY_DRIFT")
    for binding in [p["source"] for p in predicates] + [e["original_clause"] for e in exceptions]:
        raw, actual = snapshot.read(binding["path"])
        clause = b"".join(raw.splitlines(keepends=True)[binding["start_line"]-1:binding["end_line"]])
        if actual["sha256"] != binding["sha256"] or sha(clause) != binding["clause_sha256"]:
            raise ValueError("ORIGINAL_CLAUSE_DRIFT")
    for exception in exceptions:
        if exception["status"] != "PROPOSED_OWNER_DECISION_REQUIRED_NOT_EFFECTIVE":
            raise ValueError("UNAPPROVED_EXCEPTION_PROMOTED")
        if not all(exception[k] for k in ["reason", "responsible_role", "affected_packages", "closure_gate", "contradiction_stop"]):
            raise ValueError("UNBOUND_EXCEPTION")
    candidate = json.loads((root / CANDIDATE).read_text(encoding="utf-8"))
    for amendment in candidate["P00_CLOSURE_ACCELERATION_DECISION"]["bounded_amendment"]:
        if "replacement_clause" in amendment or amendment["operation"] != "APPEND_CLARIFICATION_ONLY" or amendment["preserve_original_verbatim"] is not True:
            raise ValueError("ACCEPTANCE_REPLACEMENT_FORBIDDEN")
    if decision["completion"] != {"R01_R08":"0/8", "release_journeys":"0/6", "provisional_weight":127, "accepted":False}:
        raise ValueError("FALSE_COMPLETION")
    if decision["context_gate"] != "ORIGINAL_128KiB_AGGREGATE_FAIL_UNCHANGED" or decision["qualified_reading"] is not False:
        raise ValueError("FALSE_CONTEXT_QUALIFICATION")
    for grant in decision["integration_grants"]:
        patch, binding = snapshot.read(grant["patch"]["path"])
        if binding["sha256"] != grant["patch"]["sha256"]:
            raise ValueError("PATCH_BINDING_DRIFT")
        with tempfile.TemporaryDirectory(prefix="p00-exact-patch-") as folder:
            temporary = Path(folder)
            subprocess.run(["git", "-C", folder, "init", "-q"], check=True, capture_output=True)
            for path in grant["exact_files"]:
                target = temporary / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(snapshot.read(path)[0])
            subprocess.run(["git", "-C", folder, "apply", "--unidiff-zero", "-"], input=patch, check=True, capture_output=True)
            for path in grant["exact_files"]:
                expected = (temporary / path).read_bytes().replace(b"\r\n", b"\n")
                actual = (root / path).read_bytes().replace(b"\r\n", b"\n")
                if actual != expected or sha(expected) != grant["after_normalized_lf_sha256"][path]:
                    raise ValueError("OUTSIDE_EXACT_APPROVED_PATCH")
    verify_csv(root, snapshot, decision)
    return {"status":"EXACT_PATCH_ORIGINAL_CLAUSE_PRESERVATION_PASS", "accepted":False,
            "qualified_reading":False, "runtime_conformance":False, "execution_eligible":False}


if __name__ == "__main__":
    print(json.dumps(verify(Path(__file__).resolve().parents[1]), ensure_ascii=False))
