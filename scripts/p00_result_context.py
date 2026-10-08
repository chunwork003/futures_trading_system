"""候選結果閱讀索引：固定 blob 與目前檔案比對，不做 acceptance 或 lifecycle intake。"""

import argparse
import json
from pathlib import Path

try:
    from p00_context import Snapshot, bind_loaded_source
except ModuleNotFoundError:
    from scripts.p00_context import Snapshot, bind_loaded_source

INDEX = "automation/platform/result_reading_index.v1.json"


def read_results(root, planning_sha, observed_master):
    """observed_master 須由呼叫端 fresh re-entry 取得；此離線函式不證明 remote freshness。"""
    current = Snapshot(root, planning_sha)
    binding = bind_loaded_source(current, "scripts/p00_result_context.py", __file__)
    index = current.read_json(INDEX)
    if index["status"] != "CANDIDATE_NOT_AUTHORITY" or index["source_master"] != observed_master:
        raise ValueError("MASTER_DRIFT_REENTRY_REQUIRED")
    roles = [r["role"] for r in index["records"]]
    if len(set(roles)) != len(roles) or set(roles) != {"ACCEPTED_PREDECESSOR", "P01_COMPILATION", "P02_COMPILATION"}:
        raise ValueError("RESULT_INDEX_ROLE_MISMATCH")
    records = []
    for record in index["records"]:
        source = record["source"]
        snapshot = Snapshot(root, source["baseline_sha"])
        raw, actual = snapshot.read(source["path"])
        if actual != source or current.read(source["path"])[1]["git_blob"] != actual["git_blob"]:
            raise ValueError("RESULT_SOURCE_DRIFT")
        value = json.loads(raw)
        if record["role"] == "ACCEPTED_PREDECESSOR":
            if value.get("package_id") != "AUTO-IMP-002" or value.get("status") != "ACCEPTED_MATERIALIZED":
                raise ValueError("PREDECESSOR_STATUS_MISMATCH")
            if Snapshot(root, observed_master).read(source["path"])[1]["git_blob"] != actual["git_blob"]:
                raise ValueError("PREDECESSOR_NOT_IN_MASTER")
            disposition = "ACCEPTED_PREDECESSOR_REFERENCE_ONLY_NOT_NEW_AUTHORITY"
        else:
            pid = record["role"].split("_")[0]
            candidate = current.read_json(f"docs/program/packages/{pid}.candidate.v1.json")
            if value.get("package") != candidate or value.get("execution_eligible") is not False:
                raise ValueError("COMPILATION_CANDIDATE_DRIFT")
            if value.get("status") != "PACKAGE_NOT_READY":
                raise ValueError("UNEXPECTED_COMPILATION_STATUS")
            disposition = "HISTORICAL_COMPILATION_RECOMPILE_CURRENT_CONTEXT_BEFORE_USE"
        records.append({"role": record["role"], "source": actual, "disposition": disposition})
    return {"authority": "NONE_READING_ONLY", "execution_eligible": False,
            "tool_binding": binding, "index_source": current.read(INDEX)[1],
            "planning_sha": planning_sha, "observed_master": observed_master,
            "records": records, "complete_current_intake": False,
            "unresolved": ["PENDING_RESULT_DISCOVERY", "OPEN_REVIEW_DISCOVERY", "STOP_DISCOVERY",
                           "CURRENT_CONTEXT_RECOMPILATION", "INDEPENDENT_REVIEW"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--planning", required=True)
    parser.add_argument("--observed-master", required=True)
    args = parser.parse_args()
    print(json.dumps(read_results(args.root, args.planning, args.observed_master), indent=2))


if __name__ == "__main__":
    main()
