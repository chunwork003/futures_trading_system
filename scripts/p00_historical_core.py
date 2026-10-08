"""GAP-08 accepted scope 與 V1 delta 的來源核對；不計產品 credit，不重開 acceptance。"""

import json
from pathlib import Path
import re

from p00_context import Snapshot
from p00_progress import calculate


def reconcile(registry, ledger, snapshot):
    """以 exact Git blob/table/closure 保留歷史權重；新整合 evidence 必須另行 intake。"""
    def require(condition, reason):
        if not condition:
            raise ValueError(reason)

    require(registry["source_master"] == snapshot.baseline, "SOURCE_MASTER_MISMATCH")
    require(registry["historical_scope"] == "GAP08_CORRECTION_CORE_ONLY", "HISTORICAL_SCOPE_CHANGED")
    require(ledger["source_master"] == snapshot.baseline, "DELTA_LEDGER_BASELINE_MISMATCH")
    calculate(ledger)
    require(registry["status"] == "CANDIDATE_SOURCE_RECONCILIATION_NOT_PRODUCT_ACCEPTANCE"
            and registry["authority"] == "NONE", "NO_NEW_ACCEPTANCE_AUTHORITY")
    sources = {}
    for source in registry["source_evidence"]:
        require(source["path"] not in sources and source["baseline_sha"] == snapshot.baseline,
                "SOURCE_DUPLICATE_OR_STALE")
        raw, evidence = snapshot.read(source["path"])
        require(source["git_blob"] == evidence["git_blob"] and source["sha256"] == evidence["sha256"],
                "SOURCE_BLOB_MISMATCH")
        sources[source["path"]] = raw.decode("utf-8-sig")
    table_path = "docs/work/GAP08_CORRECTION_FREEZE.md"
    accepted_ids = {f"C{i:02}" for i in range(1, 26)} | {"V06"}
    table = {}
    for line in sources[table_path].splitlines():
        cells = [part.strip() for part in line.split("|")[1:-1]]
        if cells and cells[0] in accepted_ids:
            require(cells[0] not in table, "SOURCE_LEAF_DUPLICATE")
            table[cells[0]] = (cells[1], int(cells[3] if cells[0].startswith("C") else cells[2]))
    require(set(table) == accepted_ids, "SOURCE_CORE_INCOMPLETE")
    closure = sources["docs/work/GAP08_FINAL_CLOSURE.md"]
    require(re.search(r"GAP08\s*=\s*CLOSED_ACCEPTED", closure) is not None
            and re.search(r"GAP08_CORRECTION_CORE\s*=\s*113 / 113 ACCEPTED", closure) is not None,
            "ACCEPTED_CLOSURE_MISSING")
    runtime = registry["accepted_runtime_head"]
    require(re.fullmatch(r"[0-9a-f]{40}", runtime) is not None
            and re.search(r"GAP08_RUNTIME_ACCEPTED_HEAD\s*=\s*" + runtime, closure) is not None,
            "ACCEPTED_RUNTIME_MISMATCH")
    snapshot.git("merge-base", "--is-ancestor", runtime, snapshot.baseline)
    deliverables = {row["id"] for row in ledger["deliverables"]}
    rows = registry["core"]
    require(len(rows) == len(accepted_ids) and {row["id"] for row in rows} == accepted_ids,
            "CORE_COUNT_OR_ID_MISMATCH")
    total = 0
    for row in rows:
        require(type(row["accepted_scope_weight"]) is int
                and (row["name"], row["accepted_scope_weight"]) == table[row["id"]], "HISTORICAL_WEIGHT_CHANGED")
        require(row["historical_acceptance"] == "ACCEPTED_FOR_GAP08_SCOPE"
                and type(row["new_v1_credit"]) is int and row["new_v1_credit"] == 0,
                "HISTORICAL_ACCEPTANCE_IS_NOT_NEW_V1_CREDIT")
        pointer = row["source_row"]
        require(pointer["path"] == table_path and type(pointer["line"]) is int and pointer["line"] > 0
                and sources[table_path].splitlines()[pointer["line"] - 1] == pointer["text"], "ROW_SOURCE_MISMATCH")
        require(pointer["text"].split("|")[1].strip() == row["id"], "ROW_ID_MISMATCH")
        require(row["acceptance_source"] == "docs/work/GAP08_FINAL_CLOSURE.md", "ACCEPTANCE_SOURCE_MISMATCH")
        links = row["v1_delta_deliverables"]
        require(links and len(links) == len(set(links)) and set(links) <= deliverables, "UNKNOWN_DELTA_LINK")
        require(isinstance(row["remaining_boundary"], str) and row["remaining_boundary"], "REMAINING_BOUNDARY_MISSING")
        total += row["accepted_scope_weight"]
    require(registry["totals"] == {"leaf_count": 26, "accepted_scope_weight": total, "new_v1_credit": 0}
            and total == 113, "WEIGHT_IS_NOT_LEAF_COUNT")
    require(registry["full_historical_requirement_coverage"] == "INCOMPLETE"
            and registry["v1_weight_baseline_accepted"] is False
            and registry["trusted_progress_intake"] == "NOT_IMPLEMENTED"
            and registry["product_completion"] == "UNCALIBRATED", "PRODUCT_CALIBRATION_NOT_ESTABLISHED")
    require(registry["excluded"] == {
        "original_35_151_candidate": "NOT_RETROACTIVELY_ACCEPTED_NO_CREDIT",
        "V01_V05": "SEPARATE_BROKER_VERIFICATION_WEIGHT_19_NOT_GRANTED",
        "V07": "ACTUAL_ENVIRONMENT_CONFORMANCE_WEIGHT_4_NOT_EXECUTED_NOT_VERIFIED",
        "isolated_W4R_PG": "ACCEPTED_LIMITED_EXISTING_TEST_SCOPE_NOT_ALL_V1_DB_DEPENDENCIES"},
        "HISTORICAL_EXCLUSIONS_CHANGED")
    return {"status": "EXACT_SOURCE_RECONCILIATION_PASS", **registry["totals"],
            "product_completion": "UNCALIBRATED", "execution_eligible": False,
            "independent_review": "NOT_PERFORMED"}


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    registry = json.loads((root / "docs/program/accepted_core_reconciliation.v1.json").read_text(encoding="utf-8"))
    ledger = json.loads((root / "docs/program/program_baseline.v1.json").read_text(encoding="utf-8"))
    print(json.dumps(reconcile(registry, ledger, Snapshot(root, registry["source_master"]))))
