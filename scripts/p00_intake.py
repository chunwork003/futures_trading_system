"""候選 intake 觀測與純規格路由；不寫 receipt、不接受工作、不 dispatch。"""

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

try:
    from p00_context import Snapshot, bind_loaded_source
except ModuleNotFoundError:
    from scripts.p00_context import Snapshot, bind_loaded_source

SCHEMA = "automation/platform/intake_observation.schema.v1.json"
CURRENT = "automation/work_orders/CURRENT_CODEX.yaml"
ORDER = [("stop", "HANDLE_STOP"), ("active_execution", "REVALIDATE_EXECUTION_LINEAGE"),
         ("active_writer", "RESOLVE_WRITER_OWNERSHIP"), ("pending_result", "INTAKE_RESULT"),
         ("pending_review", "ORCHESTRATE_REVIEW"), ("pending_integration", "CHECK_INTEGRATION"),
         ("pending_acceptance", "CHECK_ACCEPTANCE"), ("latest_delta", "READ_DELTA"),
         ("last_accepted_result", "READ_ACCEPTED_BASELINE")]


def propose(observation, schema):
    """規格 oracle：證據可信性／授權不是此純函式能建立的事實。"""
    Draft202012Validator(schema).validate(observation)
    route = "EVALUATE_AUTHORITY_AND_DEPENDENCIES"
    reason = "ALL_PRIOR_OBSERVATIONS_EXPLICIT"
    for field, action in ORDER:
        item = observation["observations"][field]
        if item["knowledge"] == "UNKNOWN":
            route, reason = "REHYDRATE_MISSING_EVIDENCE", field
            break
        if item["knowledge"] == "PRESENT":
            route, reason = action, field
            break
    return {"proposal": route, "reason": reason, "authority": "NONE_PLANNING_ONLY",
            "execution_eligible": False, "evidence_trust_verified": False,
            "side_effects": "NONE"}


def observe(root, planning, observed_master):
    """只從本 baseline 明確空 writer/execution 欄位建觀測；未知欄位不猜 NONE。"""
    snapshot = Snapshot(root, planning)
    binding = bind_loaded_source(snapshot, "scripts/p00_intake.py", __file__)
    policy = snapshot.read_json("automation/platform/context_policy.v1.json")
    if policy["source_baseline_sha"] != observed_master:
        raise ValueError("MASTER_DRIFT_REENTRY_REQUIRED")
    source = Snapshot(root, observed_master)
    raw, evidence = source.read(CURRENT)
    if snapshot.read(CURRENT)[1]["git_blob"] != evidence["git_blob"]:
        raise ValueError("CURRENT_SOURCE_DRIFT")
    current = json.loads(raw)
    values = {field: {"knowledge": "UNKNOWN", "scope": "CURRENT_PROGRAM", "items": [],
                      "evidence": [], "reason": "NO_EXHAUSTIVE_CURRENT_REGISTRY_BINDING"}
              for field, _ in ORDER}
    # 明確 null 且相互一致才能表示這個已綁定 operational projection 的 NONE。
    groups = {"active_execution": ("execution_id", "current_execution_id", "active_execution_id"),
              "active_writer": ("active_writer", "writer_owner")}
    for field, keys in groups.items():
        if all(k in current and current[k] is None for k in keys) and (
                field != "active_writer" or current.get("writer_state") == "NONE") and (
                current.get("status") == "CANDIDATE_NOT_AUTHORIZED" and
                current.get("executor_invoked") is False and current.get("dispatch_committed") is False):
            refs = [{k: evidence[k] for k in ("path", "git_blob", "sha256")} | {"json_pointer": "/" + key}
                    for key in keys]
            if field == "active_writer":
                refs.append({k: evidence[k] for k in ("path", "git_blob", "sha256")} | {"json_pointer": "/writer_state"})
            values[field] = {"knowledge": "NONE", "scope": "CURRENT_PROGRAM", "items": [],
                             "evidence": refs, "reason": "EXPLICIT_EMPTY_BOUND_OPERATIONAL_PROJECTION_NOT_OS_PROCESS_ATTESTATION"}
    observation = {"schema_version": "p00.intake_observation.v1", "authority": "NONE_PLANNING_ONLY",
                   "execution_eligible": False, "source_master": observed_master, "observations": values}
    schema = snapshot.read_json(SCHEMA)
    return {"observation": observation, "route": propose(observation, schema), "tool_binding": binding,
            "schema_source": snapshot.read(SCHEMA)[1], "current_source": evidence,
            "complete_current_intake": False,
            "limitations": ["Caller must obtain fresh remote master; this tool is offline.",
                            "Existing accepted WORK re-entry still required; missing registries remain UNKNOWN.",
                            "No invocation, resume, receipt, independent acceptance or OS writer attestation."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--planning", required=True)
    parser.add_argument("--observed-master", required=True)
    args = parser.parse_args()
    print(json.dumps(observe(args.root, args.planning, args.observed_master), indent=2))


if __name__ == "__main__":
    main()
