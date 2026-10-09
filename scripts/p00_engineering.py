"""P00工程系統候選的來源／型別／measurement反例檢查；不做可信intake或qualification。"""

from decimal import Decimal, localcontext
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, FormatChecker

from p00_context import Snapshot, canonical

DELIVERY_IDS = {f"OWNER-084-DELIVERABLE-{i:02}" for i in (24, 25, 26, 27, 28, 29, 30, 38, 39, 43)}
CONFIG_KEYS = {"schema_version", "revision", "status", "authority", "source_master", "source_candidate",
               "source_evidence", "owner_delivery_clause_ids", "design_owner", "templates", "generators", "patterns",
               "golden_tasks", "kpis", "telemetry", "optimization", "roadmap", "independent_review",
               "actual_golden_qualification", "new_v1_credit", "runtime_or_controller_effects"}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def validate_shape(schema, value):
    """含format檢查的closed schema；shape不能證明producer identity或independent review。"""
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
                    key=lambda e: repr(list(e.path)))
    if errors:
        raise ValueError(f"ENGINEERING_SCHEMA_INVALID:{list(errors[0].path)}:{errors[0].message}")


def bind_ref(reference, snapshots):
    require(set(reference) == {"path", "baseline_sha", "git_blob", "sha256", "size_bytes"}, "SOURCE_REF_FIELDS_INVALID")
    require(reference["baseline_sha"] in snapshots, "SOURCE_SNAPSHOT_NOT_DECLARED")
    raw, actual = snapshots[reference["baseline_sha"]].read(reference["path"])
    require(canonical(reference) == canonical(actual), "SOURCE_REF_BLOB_MISMATCH")
    return raw


def code_list(owner, number):
    body = re.search(rf"^# {number}\. .+?(?=^# \d+\. |\Z)", owner, re.M | re.S)
    require(body is not None, "OWNER_SECTION_MISSING")
    block = re.search(r"```text\r?\n(.*?)```", body[0], re.S)
    require(block is not None, "OWNER_CODE_LIST_MISSING")
    return [line.strip() for line in block[1].splitlines() if line.strip()]


def verify_config(config, candidate, master):
    """核對exact source／原始義務與候選status，不把策略文件當已運作能力。"""
    require(set(config) == CONFIG_KEYS and type(config["revision"]) is int and config["revision"] == 1,
            "ENGINEERING_CONFIG_FIELDS_INVALID")
    require(config["schema_version"] == "p00.engineering_system.v1"
            and config["source_candidate"] == candidate.baseline and config["source_master"] == master.baseline,
            "ENGINEERING_CONFIG_BASELINE_MISMATCH")
    candidate.git("merge-base", "--is-ancestor", master.baseline, candidate.baseline)
    require(config["status"] == "CANDIDATE_AUTHORED_NOT_ACCEPTED" and config["authority"] == "NONE"
            and config["independent_review"] == "NOT_PERFORMED" and config["actual_golden_qualification"] == "NOT_RUN"
            and type(config["new_v1_credit"]) is int and config["new_v1_credit"] == 0
            and config["runtime_or_controller_effects"] == "NONE", "CANDIDATE_NOT_ACCEPTANCE_OR_ACTIVATION")
    snapshots = {candidate.baseline: candidate, master.baseline: master}
    sources = {}
    for row in config["source_evidence"]:
        require(row["path"] not in sources, "SOURCE_REF_DUPLICATE")
        bind_ref(row, snapshots)
        sources[row["path"]] = row
    registry = candidate.read_json("docs/program/historical_requirements.v1.json")
    require({"docs/program/P00_OWNER_REQUEST.md", "docs/program/historical_requirements.v1.json",
             "docs/program/current_truth.v1.json", "automation/platform/skill_registry.v1.json"} <= set(sources),
            "MANDATORY_ENGINEERING_SOURCE_MISSING")
    require(len(config["owner_delivery_clause_ids"]) == 10 and set(config["owner_delivery_clause_ids"]) == DELIVERY_IDS,
            "TEN_DELIVERY_CLAUSES_MISSING_OR_DUPLICATE")
    require(DELIVERY_IDS <= {row["id"] for row in registry["owner_clause_catalog"]}, "DELIVERY_NOT_IN_SOURCE_REGISTRY")
    owner = candidate.read("docs/program/P00_OWNER_REQUEST.md")[0].decode("utf-8-sig")
    for group in ("templates", "generators", "patterns", "golden_tasks", "kpis", "roadmap"):
        require(len({row["id"] for row in config[group]}) == len(config[group]), "ENGINEERING_COMPONENT_DUPLICATE")
    require(len(config["templates"]) == 10 and len(config["patterns"]) == 5, "TEMPLATE_OR_PATTERN_SET_INCOMPLETE")
    require({r["id"] for r in config["templates"]} == {"T-" + kind for kind in (
        "package", "architecture-decision", "api-contract", "state-machine", "migration-plan", "review",
        "incident", "release", "execution-result", "handoff")}, "TEMPLATE_KIND_SET_INCOMPLETE")
    require({r["id"] for r in config["generators"]} == {"GEN-" + kind for kind in (
        "package", "openapi-dto", "context", "reading-pack", "source-index", "progress", "test-review-matrix",
        "migration-checklist", "current-projection", "typescript-csharp-client")}, "GENERATOR_KIND_SET_INCOMPLETE")
    for row in config["templates"]:
        require(row["default_disposition"] == "CANDIDATE_DRAFT_NOT_ACCEPTED" and row["qualification"] == "NOT_QUALIFIED"
                and row["required_fields"] and row["reference_paths"], "TEMPLATE_CANNOT_PREFILL_ACCEPTANCE")
        require(set(row["reference_paths"]) <= set(sources), "TEMPLATE_REFERENCE_NOT_BOUND")
    for row in config["generators"]:
        require(row["reference_path"] in sources and row["generated_semantics"] == "NONE_AUTHOR_PROVIDED_ONLY"
                and row["allowed_effects"] == "P00_CANDIDATE_ARTIFACT_ONLY", "GENERATOR_CANNOT_CREATE_SEMANTICS_OR_AUTHORITY")
    for row in config["patterns"]:
        require(set(row["reference_paths"]) <= set(sources) and row["positive_obligation"] and row["counterexamples"],
                "PATTERN_REFERENCE_OR_COUNTEREXAMPLE_MISSING")
        require(row["actual_product_slice"] in {"UNIMPLEMENTED", "NEW_DELTA_UNIMPLEMENTED", "NOT_APPLICABLE"},
                "PATTERN_IS_NOT_VERIFIED_PRODUCT_SLICE")
    tasks = config["golden_tasks"]
    require([row["id"] for row in tasks] == [f"G{i:02}" for i in range(1, 10)]
            and [row["task_family"] for row in tasks] == code_list(owner, 40), "NINE_GOLDEN_FAMILIES_INCOMPLETE")
    for row in tasks:
        require(row["source_clause_id"] == f"OWNER-040-GOLDEN-{int(row['id'][1:]):02}"
                and row["positive_oracle"] and row["counterexamples"] and row["qualification_gate"]
                and row["actual_evaluation_status"] == "NOT_RUN", "GOLDEN_TASK_NOT_ACTUALLY_QUALIFIED")
        require(row["candidate_fixture_path"] in sources and row["candidate_oracle_path"] in sources
                and row["reference_scope"] == "CANDIDATE_CONTRACT_REFERENCE_ONLY_NOT_REPRESENTATIVE_TASK_EXECUTION",
                "GOLDEN_REFERENCE_SCOPE_UNBOUND")
    require([row["name"] for row in config["kpis"]] == code_list(owner, 41), "KPI_POPULATION_INCOMPLETE")
    for row in config["kpis"]:
        require(row["formula"] and row["required_quality"] == "TRUSTED_COMPLETE_MATCHED_POPULATION"
                and row["current_qualified_value"] is None and row["unknown_reason"], "KPI_QUALIFICATION_NOT_ESTABLISHED")
    telemetry = config["telemetry"]
    require(telemetry["unknown_is_not_zero"] is True and telemetry["trusted_intake"] == "NOT_IMPLEMENTED"
            and telemetry["account_quota"] == "SHARED_ACCOUNT_PROXY_PERCENT_ONLY_NOT_ACTOR_COST", "TELEMETRY_TRUST_NOT_ESTABLISHED")
    metrics = code_list(owner, 68)
    require(telemetry["skill_metrics"] + telemetry["agent_metrics"] == metrics, "SKILL_AGENT_METRICS_INCOMPLETE")
    optimization = config["optimization"]
    require(optimization["current_roi"] is None and optimization["current_effectiveness"] == "UNKNOWN"
            and optimization["product_effort_target_verified"] is False and optimization["activation"] == "NOT_ENABLED",
            "OPTIMIZATION_GAIN_OR_ACTIVATION_NOT_ESTABLISHED")
    require(optimization["states"] == ["OBSERVED", "CLASSIFIED", "ROOT_CAUSE_PROPOSED", "IMPROVEMENT_PROPOSED",
            "SHADOW_EVAL", "INDEPENDENT_REVIEW", "BOUNDED_ADOPTION", "VERSIONED_PROMOTION"],
            "OPTIMIZATION_REVIEW_STAGE_CANNOT_BE_SKIPPED")
    require([row["id"] for row in config["roadmap"]] == [f"D{i}" for i in range(6)]
            and all(row["product_must_wait_for_all_phases"] is False for row in config["roadmap"]), "ROADMAP_MUST_NOT_STALL_PRODUCT")
    require([row["current_status"] for row in config["roadmap"]] == ["CANDIDATE_SOURCE_INDEXED",
            "CANDIDATE_AUTHORED_NOT_ACCEPTED", "PROTOTYPES_ONLY", "NOT_IMPLEMENTED_NOT_ENABLED",
            "NOT_QUALIFIED", "NOT_QUALIFIED"], "ROADMAP_QUALIFICATION_NOT_ESTABLISHED")
    return {"status": "CANDIDATE_SOURCE_AND_OBLIGATION_CHECK_PASS", "source_refs": len(sources),
            "delivery_clauses": 10, "golden_families": 9, "kpis": len(config["kpis"]),
            "qualification": "NOT_QUALIFIED", "actual_golden_runs": 0, "new_v1_credit": 0, "execution_eligible": False}


def read_pointer(value, pointer):
    """嚴格JSON pointer，只讀source scalar；不把匹配scalar當producer completeness。"""
    for part in pointer.split("/")[1:]:
        require(re.search(r"~(?![01])", part) is None, "SOURCE_POINTER_ESCAPE_INVALID")
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            require(re.fullmatch(r"0|[1-9]\d*", part) is not None and int(part) < len(value), "SOURCE_POINTER_NOT_FOUND")
            value = value[int(part)]
        else:
            require(isinstance(value, dict) and part in value, "SOURCE_POINTER_NOT_FOUND")
            value = value[part]
    return value


def validate_observation(event, schema, snapshots):
    validate_shape(schema, event)
    names = set()
    for row in event["measurements"]:
        name = row["name"]
        require(name not in names, "MEASUREMENT_NAME_DUPLICATE")
        names.add(name)
        unit = "PERCENT" if name == "ACCOUNT_USAGE_PERCENT" else "WEIGHT" if name == "ACCEPTED_WEIGHT" else (
            "TOKENS" if "TOKENS" in name else "BYTES" if name == "CONTEXT_BYTES" else "SECONDS" if "SECONDS" in name else "COUNT")
        require(row["unit"] == unit, "MEASUREMENT_UNIT_MISMATCH")
        if name == "ACCOUNT_USAGE_PERCENT":
            require(row["scope"] == "SHARED_ACCOUNT_PROXY", "ACCOUNT_QUOTA_NOT_ACTOR_COST")
        if name.startswith("ACTUAL_ACTOR_") or name == "ACCEPTED_WEIGHT":
            require(row["status"] in {"NOT_AVAILABLE", "NOT_APPLICABLE"}, "ACTOR_TOKEN_OR_ACCEPTANCE_TRUSTED_INTAKE_NOT_IMPLEMENTED")
        if name.startswith("EXPECTED_"):
            require(row["status"] != "OBSERVED", "FORECAST_IS_ESTIMATE_NOT_ACTUAL")
        elif name.startswith("ACTUAL_"):
            require(row["status"] != "ESTIMATED", "ESTIMATE_IS_NOT_ACTUAL")
        if row["value"] is not None:
            number = Decimal(row["value"])
            require(number.is_finite() and number >= 0, "MEASUREMENT_NONFINITE_OR_NEGATIVE")
            if unit in {"TOKENS", "BYTES", "COUNT"}:
                require(number == number.to_integral_value(), "COUNT_BYTES_TOKENS_NOT_FRACTIONAL")
            if unit == "PERCENT":
                require(number <= 100, "ACCOUNT_PERCENT_OUT_OF_RANGE")
            if row["status"] == "OBSERVED":
                raw = bind_ref(row["source_ref"], snapshots)
                scalar = read_pointer(json.loads(raw.decode("utf-8-sig"), parse_float=Decimal), row["source_pointer"])
                require(type(scalar) in {int, str, Decimal} and re.fullmatch(r"(?:0|[1-9]\d*)(?:\.\d+)?", str(scalar)),
                        "SOURCE_SCALAR_NOT_MEASUREMENT")
                require(Decimal(str(scalar)) == number, "SOURCE_MEASUREMENT_VALUE_MISMATCH")
    return {"source_scalar_shape": "PASS", "producer_qualification": "NOT_QUALIFIED",
            "accepted_work_metrics": "UNKNOWN", "task_token_actual": "NOT_AVAILABLE"}


def observation_preview(events, schema, snapshots):
    """去重spec records；不計qualified rates、不保存append-only store。"""
    unique = {}
    for event in events:
        validate_observation(event, schema, snapshots)
        key, body = event["event_id"], canonical(event)
        require(key not in unique or unique[key] == body, "EVENT_ID_PAYLOAD_CONFLICT")
        unique[key] = body
    return {"canonical_spec_record_count": len(unique), "qualification": "NOT_QUALIFIED",
            "population_completeness": "UNKNOWN", "accepted_weight": None, "effectiveness": "UNKNOWN"}


def validate_evaluation(trial, schema, config, snapshots):
    validate_shape(schema, trial)
    require(trial["input_snapshot"] == config["source_candidate"], "GOLDEN_INPUT_SNAPSHOT_DRIFT")
    task = next(row for row in config["golden_tasks"] if row["id"] == trial["task_family_id"])
    references = {row["path"]: row for row in config["source_evidence"]}
    for role in ("fixture", "oracle"):
        expected = references[task[f"candidate_{role}_path"]]
        require(canonical(trial[f"{role}_ref"]) == canonical(expected), "GOLDEN_FAMILY_REFERENCE_MISMATCH")
        bind_ref(trial[f"{role}_ref"], snapshots)
    expected_cases = {task["id"] + "-POS", *(task["id"] + f"-NEG-{i:02}" for i in range(1, len(task["counterexamples"]) + 1))}
    for side in (trial["baseline"], trial["candidate"]):
        require(side["subject_sha"] in snapshots, "GOLDEN_SUBJECT_SNAPSHOT_NOT_DECLARED")
        require(side["fixture_sha256"] == trial["fixture_ref"]["sha256"]
                and side["oracle_sha256"] == trial["oracle_ref"]["sha256"], "GOLDEN_ORACLE_OR_FIXTURE_DRIFT")
        require(len(side["cases"]) == len(expected_cases) and {r["case_id"] for r in side["cases"]} == expected_cases,
                "MANDATORY_GOLDEN_CASE_SET_INCOMPLETE_OR_DUPLICATE")
        for row in side["cases"]:
            require((row["artifact_sha256"] is not None) == row["declared_outcome"].startswith("DECLARED_"),
                    "DECLARED_OUTCOME_ARTIFACT_REQUIRED_NO_NOT_RUN_ARTIFACT")
    for key in ("environment_id", "fixture_sha256", "oracle_sha256", "contract_revision"):
        require(trial["baseline"][key] == trial["candidate"][key], "UNMATCHED_GOLDEN_COHORT")
    return {"status": "SHADOW_SHAPE_AND_BOUND_REFERENCES_PASS", "task_family": task["id"],
            "qualification": "NOT_QUALIFIED", "effectiveness": "UNKNOWN", "independent_review": "NOT_PERFORMED"}


def forecast_error_preview(forecast, actual, matched_scope):
    """有界spec算術；caller flag不證明真實coverage，actual0不造成division by zero。"""
    if forecast is None or actual is None or matched_scope is not True:
        return {"absolute_error": None, "relative_error": None, "reason": "MISSING_OR_UNMATCHED_INPUTS", "qualified": False}
    require(isinstance(forecast, str) and isinstance(actual, str)
            and len(forecast) <= 40 and len(actual) <= 40
            and re.fullmatch(r"(?:0|[1-9]\d*)(?:\.\d+)?", forecast)
            and re.fullmatch(r"(?:0|[1-9]\d*)(?:\.\d+)?", actual), "PREVIEW_DECIMAL_INPUT_INVALID")
    with localcontext() as context:
        context.prec = 90
        expected, observed = Decimal(forecast), Decimal(actual)
        error = abs(observed - expected)
        return {"absolute_error": str(error), "relative_error": str(error / observed) if observed else None,
                "reason": "SPEC_ARITHMETIC_ONLY" if observed else "ZERO_ACTUAL_RELATIVE_UNDEFINED", "qualified": False}


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    platform = root / "automation/platform"
    config = json.loads((platform / "engineering_system.v1.json").read_text(encoding="utf-8"))
    candidate, master = Snapshot(root, config["source_candidate"]), Snapshot(root, config["source_master"])
    snapshots = {candidate.baseline: candidate, master.baseline: master}
    result = verify_config(config, candidate, master)
    fixtures = json.loads((platform / "engineering_system.fixture.v1.json").read_text(encoding="utf-8"))
    observation_schema = json.loads((platform / "engineering_observation.schema.v1.json").read_text(encoding="utf-8"))
    evaluation_schema = json.loads((platform / "golden_evaluation.schema.v1.json").read_text(encoding="utf-8"))
    result["observation_preview"] = observation_preview([fixtures["observation"]], observation_schema, snapshots)
    result["evaluation_shape_checks"] = [validate_evaluation(t, evaluation_schema, config, snapshots) for t in fixtures["evaluation_shapes"]]
    print(json.dumps(result, ensure_ascii=True, indent=2))
