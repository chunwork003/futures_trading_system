"""P00 候選 wire contracts 的單一可重建來源；不建立 server 或 execution authority。"""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/architecture/contracts"


def ref(name):
    return {"$ref": f"#/components/schemas/{name}"}


def enum(*values):
    return {"type": "string", "enum": list(values)}


def array(item, maximum=1000):
    return {"type": "array", "items": item, "maxItems": maximum}


def nullable(schema):
    return {"anyOf": [schema, {"type": "null"}]}


def obj(properties, optional=()):
    return {"type": "object", "additionalProperties": False,
            "properties": properties, "required": [k for k in properties if k not in optional]}


def build():
    ident = {"type": "string", "pattern": "^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$"}
    digest = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    sha = {"type": "string", "pattern": "^[0-9a-f]{40}$"}
    timestamp = {"type": "string", "format": "date-time",
                 "pattern": r"^[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])T(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9](?:\.[0-9]{1,6})?Z$"}
    text = {"type": "string", "minLength": 1, "maxLength": 2048}
    rev = {"type": "integer", "minimum": 1}
    count = {"type": "integer", "minimum": 0, "maximum": 9007199254740991}
    decimal = {"type": "string", "pattern": r"^(?:0|-?[1-9][0-9]*|-?(?:0|[1-9][0-9]*)\.[0-9]*[1-9])$", "maxLength": 80}
    seed = {"type": "integer", "minimum": 0, "maximum": 4294967295}
    evidence = obj({"owner": ident, "identity": ident, "version": ident, "sha256": digest})
    schemas = {
        "Identity": ident, "Revision": rev, "Decimal": decimal, "EvidenceRef": evidence,
        "Error": obj({"code": enum("INVALID_INPUT", "UNAUTHENTICATED", "FORBIDDEN", "NOT_FOUND",
            "REVISION_CONFLICT", "IDEMPOTENCY_CONFLICT", "UNQUALIFIED_DATA", "READINESS_BLOCKED",
            "WORKLOAD_LIMIT_EXCEEDED", "DEPENDENCY_UNAVAILABLE", "INTERNAL_ERROR", "RATE_LIMITED"),
            "message": text, "correlation_id": ident, "retryable": {"type": "boolean"},
            "operation_id": nullable(ident), "current_revision": nullable(rev),
            "violations": array(obj({"field": text, "rule": ident}), 100)}),
        "DatasetVersion": obj({"dataset_id": ident, "version_id": ident, "semantic_hash": digest,
            "parent_version_id": nullable(ident), "correction_reason": nullable(text), "ingested_at": timestamp}),
        "DatasetManifest": obj({"schema_version": {"const": "dataset.v1"}, "dataset_id": ident,
            "dataset_version": ident, "canonical_content_hash": digest, "source_manifest_hash": digest,
            "calendar_version": ident, "contract_mapping_version": ident, "quality_policy_version": ident,
            "partitions": array(obj({"relative_path": {"type": "string", "pattern": r"^partitions/[a-zA-Z0-9_-]+\.parquet$"},
                "byte_hash": digest, "row_count": count, "first_open_at": timestamp, "last_open_at": timestamp}), 10000),
            "coverage": obj({"start_at": timestamp, "end_at": timestamp, "required_bars": count,
                "observed_bars": count, "missing_bars": count, "conflicting_bars": count}),
            "accepted_quality_report": ref("EvidenceRef")}),
        "ContractBinding": obj({"instrument_id": rev, "contract_id": rev,
            "calendar_ref": ref("EvidenceRef"), "mapping_ref": ref("EvidenceRef")}),
        "StrategyDefinition": obj({"strategy_id": ident, "implementation_revision": ident,
            "config_schema_ref": ref("EvidenceRef"), "supported_timeframes": array(ident, 20),
            "supported_modes": array(enum("BACKTEST", "SIMULATED"), 2)}),
        "StrategyBinding": obj({"strategy_id": ident, "implementation_revision": ident,
            "instance_id": ident, "config_ref": ref("EvidenceRef"), "contract": ref("ContractBinding"),
            "timeframe": ident}),
        "RunBindings": obj({"dataset": ref("EvidenceRef"), "strategies": {**array(ref("StrategyBinding"), 20), "minItems": 1},
            "decision_policy": ref("EvidenceRef"), "risk_policy": ref("EvidenceRef"),
            "cost_policy": ref("EvidenceRef"), "margin_policy": ref("EvidenceRef"),
            "code_sha": sha, "dependency_lock_hash": digest, "seed": seed,
            "rng_algorithm": {"const": "PCG64"}, "rng_version": ident}),
        "BacktestSpec": obj({"kind": {"const": "BACKTEST"}}),
        "ParameterStudySpec": obj({"kind": {"const": "PARAMETER_STUDY"},
            "trial_config_refs": {**array(ref("EvidenceRef"), 100), "minItems": 1, "uniqueItems": True}}),
        "OosSpec": obj({"kind": {"const": "OOS"}, "training_end_at": timestamp,
            "test_start_at": timestamp, "test_end_at": timestamp}),
        "WfoSpec": obj({"kind": {"const": "WFO"}, "training_sessions": {"type": "integer", "minimum": 20, "maximum": 1000},
            "test_sessions": {"type": "integer", "minimum": 1, "maximum": 250},
            "step_sessions": {"type": "integer", "minimum": 1, "maximum": 250},
            "max_folds": {"type": "integer", "minimum": 1, "maximum": 20},
            "candidate_config_refs": {**array(ref("EvidenceRef"), 20), "minItems": 1},
            "selection_metric": {"const": "NET_RETURN"}, "higher_is_better": {"const": True}}),
        "MonteCarloSpec": obj({"kind": {"const": "MONTE_CARLO"}, "source_artifact": ref("EvidenceRef"),
            "method": {"const": "TRADE_RETURN_BOOTSTRAP"},
            "paths": {"type": "integer", "minimum": 1, "maximum": 1000}}),
    }
    schemas["ResearchSpec"] = {"oneOf": [ref(x) for x in ("BacktestSpec", "ParameterStudySpec", "OosSpec", "WfoSpec", "MonteCarloSpec")],
                               "discriminator": {"propertyName": "kind"}}
    schemas["ResearchRunRequest"] = obj({"bindings": ref("RunBindings"), "spec": ref("ResearchSpec"),
        "initial_capital": decimal, "currency": {"const": "TWD"}})
    schemas["ResearchRunRequest"]["properties"]["initial_capital"] = {**decimal, "pattern": r"^(?:[1-9][0-9]*|(?:0|[1-9][0-9]*)\.[0-9]*[1-9])$"}
    schemas["ResearchRun"] = obj({"run_id": ident, "operation_id": ident, "request": ref("ResearchRunRequest"),
        "input_fingerprint": digest, "created_by": ident, "created_at": timestamp})
    schemas["CommandReceipt"] = obj({"command_id": ident, "idempotency_key": ident,
        "request_fingerprint": digest, "resource_id": ident, "resource_revision": nullable(rev),
        "resource_revision_status": enum("COMMITTED", "RESERVED"),
        "operation_id": nullable(ident), "outcome": enum("ACCEPTED", "ALREADY_TERMINAL"),
        "recorded_at": timestamp, "correlation_id": ident})
    schemas["CommandReceipt"]["allOf"] = [
        {"if": {"properties": {"resource_revision_status": {"const": "COMMITTED"}}},
         "then": {"properties": {"resource_revision": rev}}},
        {"if": {"properties": {"resource_revision_status": {"const": "RESERVED"}}},
         "then": {"properties": {"resource_revision": {"type": "null"}, "operation_id": ident}}}]
    schemas["Operation"] = obj({"operation_id": ident, "kind": enum("RESEARCH", "SIMULATION_COMMAND", "SIMULATION_GENESIS", "DATASET_IMPORT"),
        "resource_id": ident, "state": enum("QUEUED", "RUNNING", "CANCEL_REQUESTED", "RETRY_WAIT", "SUCCEEDED", "FAILED", "CANCELLED"),
        "revision": rev, "request_fingerprint": digest, "command_id": ident,
        "current_attempt_id": nullable(ident), "created_at": timestamp, "updated_at": timestamp,
        "result_manifest_ids": array(ident, 100), "error": nullable(ref("Error"))})
    schemas["OperationAttempt"] = obj({"attempt_id": ident, "operation_id": ident, "attempt_no": rev,
        "worker_id": ident, "lease_generation": rev,
        "state": enum("CLAIMED", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED", "ABANDONED"),
        "started_at": timestamp, "finished_at": nullable(timestamp),
        "checkpoint_ref": nullable(ref("EvidenceRef")), "failure_code": nullable(ident)})
    schemas["WorkerLease"] = obj({"operation_id": ident, "holder_id": ident, "generation": rev,
        "expires_at": timestamp, "heartbeat_at": timestamp})
    schemas["ArtifactManifest"] = obj({"artifact_id": ident, "version": rev, "schema_version": ident,
        "media_type": enum("application/json", "application/vnd.apache.parquet", "text/csv"),
        "relative_uri": {"type": "string", "pattern": r"^sha256/[0-9a-f]{64}$"},
        "byte_hash": digest, "semantic_hash": nullable(digest), "size_bytes": count,
        "producer_run_id": ident, "producer_attempt_id": ident, "created_at": timestamp})
    schemas["Metric"] = {"oneOf": [obj({"name": ident, "value": decimal, "reason_code": {"type": "null"}}),
        obj({"name": ident, "value": {"type": "null"}, "reason_code": enum("INSUFFICIENT_SAMPLE", "ZERO_DENOMINATOR", "ZERO_VARIANCE", "NOT_APPLICABLE")})]}
    schemas["ResearchResults"] = obj({"run_id": ident, "operation_revision": rev, "input_fingerprint": digest,
        "metrics": array(ref("Metric"), 100), "artifacts": array(ref("ArtifactManifest"), 100),
        "constituent_run_ids": array(ident, 400), "assumptions_ref": ref("EvidenceRef")})
    schemas["SimulationRequest"] = obj({"mode": {"const": "SIMULATED"}, "bindings": ref("RunBindings"),
        "scenario_ref": ref("EvidenceRef"), "initial_capital": decimal, "currency": {"const": "TWD"}})
    schemas["SimulationRequest"]["properties"]["initial_capital"] = deepcopy(schemas["ResearchRunRequest"]["properties"]["initial_capital"])
    schemas["SimulationSession"] = obj({"session_id": ident, "mode": {"const": "SIMULATED"},
        "synthetic_account_id": ident, "revision": rev, "request": ref("SimulationRequest"),
        "risk_increase_blocked": {"type": "boolean"},
        "state": enum("CREATED", "STARTING", "RUNNING", "PAUSING", "PAUSED", "RECOVERING", "STOPPING", "STOPPED", "HALTED"),
        "clock_checkpoint": obj({"occurred_at": timestamp, "event_index": count}),
        "created_at": timestamp, "governing_refs": array(ref("EvidenceRef"), 20)})
    schemas["SimulationCommand"] = obj({"command": enum("START", "PAUSE", "STOP", "RECOVER", "KILL", "FORCE_FLAT"),
        "reason": text})
    schemas["CancelRequest"] = obj({"reason": text})
    schemas["ImportMetadata"] = obj({"dataset_id": ident, "source_name": ident, "source_sha256": digest,
        "format": {"const": "CSV_V1"}, "calendar_ref": ref("EvidenceRef"), "mapping_ref": ref("EvidenceRef"),
        "quality_policy_ref": ref("EvidenceRef"), "parent_version_id": nullable(ident),
        "correction_reason": nullable(text)})
    schemas["DatasetImportRequest"] = obj({"metadata": ref("ImportMetadata"),
        "file": {"type": "string", "format": "binary", "description": "CSV bytes; stream maximum 256 MiB; never a path or URL."}})
    schemas["ParameterValue"] = {"oneOf": [
        obj({"kind": {"const": "INTEGER"}, "value": {"type": "integer", "minimum": -2147483648, "maximum": 2147483647}}),
        obj({"kind": {"const": "DECIMAL"}, "value": decimal}),
        obj({"kind": {"const": "BOOLEAN"}, "value": {"type": "boolean"}}),
        obj({"kind": {"const": "TEXT"}, "value": {"type": "string", "maxLength": 256}})]}
    schemas["StrategyConfigRequest"] = obj({"strategy_id": ident, "implementation_revision": ident,
        "config_schema_ref": ref("EvidenceRef"),
        "parameters": array(obj({"name": ident, "value": ref("ParameterValue")}), 100)})
    schemas["StrategyConfigVersion"] = obj({"strategy_id": ident, "config_version": ident,
        "fingerprint": digest, "request": ref("StrategyConfigRequest"), "created_at": timestamp})
    schemas["ConfigurationCatalog"] = obj({"strategies": array(ref("StrategyDefinition"), 100),
        "strategy_configs": array(ref("EvidenceRef"), 1000), "decision_policies": array(ref("EvidenceRef"), 100),
        "risk_policies": array(ref("EvidenceRef"), 100), "cost_policies": array(ref("EvidenceRef"), 100),
        "margin_policies": array(ref("EvidenceRef"), 100), "scenarios": array(ref("EvidenceRef"), 100),
        "calendars": array(ref("EvidenceRef"), 100), "contract_mappings": array(ref("EvidenceRef"), 100),
        "quality_policies": array(ref("EvidenceRef"), 100)})
    schemas["ResolveCaseRequest"] = obj({"resolution_note": text})
    schemas["ResultCell"] = {"oneOf": [
        obj({"kind": {"const": "DECIMAL"}, "value": decimal}),
        obj({"kind": {"const": "INTEGER"}, "value": {"type": "integer", "minimum": -9007199254740991, "maximum": 9007199254740991}}),
        obj({"kind": {"const": "TEXT"}, "value": {"type": "string", "maxLength": 256}}),
        obj({"kind": {"const": "INSTANT"}, "value": timestamp}),
        obj({"kind": {"const": "BOOLEAN"}, "value": {"type": "boolean"}}),
        obj({"kind": {"const": "UNKNOWN"}, "reason_code": ident})]}
    schemas["ArtifactRows"] = obj({"artifact_id": ident, "artifact_hash": digest,
        "columns": array(obj({"name": ident, "kind": enum("DECIMAL", "INTEGER", "TEXT", "INSTANT", "BOOLEAN")}), 64),
        "rows": array(obj({"row_index": count, "cells": array(ref("ResultCell"), 64)})),
        "next_cursor": nullable({"type": "string", "minLength": 1, "maxLength": 4096})})
    position_fields = {"account_id": ident, "contract_id": rev, "net_quantity": {"type": "integer", "minimum": -10000, "maximum": 10000},
                       "evidence_ref": ref("EvidenceRef")}
    for name, kind in (("TargetPosition", "TARGET"), ("ExpectedPosition", "EXPECTED"), ("ActualPosition", "ACTUAL")):
        schemas[name] = obj({"kind": {"const": kind}, **position_fields})
    schemas["Position"] = {"oneOf": [ref(x) for x in ("TargetPosition", "ExpectedPosition", "ActualPosition")]}
    signed_quantity = {"type": "integer", "minimum": -10000, "maximum": 10000}
    observation = {"type": "string", "pattern": "^mor1_[0-9a-f]{64}$"}
    schemas["Signal"] = obj({"schema_version": {"const": "signal.v1"}, "signal_id": ident,
        "strategy_instance_id": ident, "strategy_version": ident, "config_version": ident,
        "instrument_id": rev, "contract_id": rev, "observation_revision_id": observation,
        "desired_net_quantity": signed_quantity, "previous_virtual_position_ref": ref("EvidenceRef"),
        "state_snapshot_ref": ref("EvidenceRef"), "correlation_id": ident})
    schemas["Decision"] = obj({"schema_version": {"const": "decision.v1"}, "decision_id": ident,
        "account_id": ident, "instrument_id": rev, "contract_id": rev, "account_revision": rev,
        "cohort_id": ident, "policy_ref": ref("EvidenceRef"), "recovery_cut_ref": ref("EvidenceRef"),
        "observation_revision_id": observation, "signal_ids": {**array(ident, 20), "minItems": 1, "uniqueItems": True},
        "expected_net_quantity": signed_quantity, "desired_net_quantity": signed_quantity,
        "proposed_net_quantity": signed_quantity,
        "action": enum("HOLD", "ADD", "REDUCE", "EXIT", "ENTER"),
        "attributions": array(obj({"strategy_instance_id": ident, "selected_net_quantity": signed_quantity,
            "signal_id": ident}), 20),
        "excluded_signals": array(obj({"signal_id": ident, "reason_code": ident}), 20), "correlation_id": ident})
    risk_common = {"schema_version": {"const": "risk_decision.v1"}, "risk_decision_id": ident,
        "decision_id": ident, "account_revision": rev, "capital_revision": rev,
        "policy_ref": ref("EvidenceRef"), "margin_ref": ref("EvidenceRef"),
        "proposed_net_quantity": signed_quantity,
        "constraint_evidence": {**array(ref("EvidenceRef"), 100), "minItems": 1},
        "reason_codes": {**array(ident, 100), "minItems": 1}}
    schemas["RiskDecision"] = {"oneOf": [obj({**risk_common, "outcome": enum("ALLOW", "REDUCE"),
        "approved_net_quantity": signed_quantity}), obj({**risk_common, "outcome": {"const": "REJECT"},
        "approved_net_quantity": {"type": "null"}})]}
    schemas["CapitalState"] = obj({"schema_version": {"const": "capital.v1"}, "capital_id": ident,
        "account_id": ident, "account_revision": rev, "revision": rev, "source": {"const": "MANUAL"},
        "currency": {"const": "TWD"}, "initial_manual_capital": deepcopy(schemas["ResearchRunRequest"]["properties"]["initial_capital"]),
        "realized_pnl": decimal, "unrealized_pnl": decimal, "fees": decimal,
        "reserved_margin": decimal, "available_capital": decimal,
        "account_checkpoint_ref": ref("EvidenceRef"), "mark_ref": ref("EvidenceRef"),
        "margin_policy_ref": ref("EvidenceRef"), "calculation_policy_ref": ref("EvidenceRef")})
    schemas["IncrementalState"] = obj({"schema_version": {"const": "incremental_state.v1"},
        "strategy_instance_id": ident, "strategy_version": ident, "config_version": ident,
        "state_schema_version": rev, "strategy_snapshot_ref": ref("EvidenceRef"),
        "feature_version_ref": ref("EvidenceRef"), "observation_revision_id": observation,
        "completed_bar_count": count, "required_warmup_bars": count,
        "warmup_status": enum("WARMING", "READY"), "state_blob_hash": digest})
    schemas["AccountState"] = obj({"account_id": ident, "environment": {"const": "SIMULATED"}, "revision": rev,
        "readiness": enum("HALT", "REVIEW", "READY"), "reason_codes": array(ident, 100),
        "expected": array(ref("ExpectedPosition"), 100),
        "actual": {"oneOf": [obj({"status": {"const": "KNOWN"}, "positions": array(ref("ActualPosition"), 100),
            "observation_ref": ref("EvidenceRef"), "completeness_ref": ref("EvidenceRef")}),
            obj({"status": {"const": "UNKNOWN"}, "reason_code": ident})]},
        "recovery_cut_ref": nullable(ref("EvidenceRef")), "trading_authorization": {"const": "SIMULATED_ONLY"}})
    schemas["ReconciliationCase"] = obj({"case_id": ident, "account_id": ident, "version": rev,
        "state": enum("HALT", "REVIEW_REQUIRED", "RESOLVED"), "policy_ref": ref("EvidenceRef"),
        "evidence_refs": array(ref("EvidenceRef"), 100), "reason_codes": array(ident, 100),
        "resolution_ref": nullable(ref("EvidenceRef"))})
    schemas["AuditEvent"] = obj({"audit_id": ident, "producer": enum("PYTHON", "APPLICATION"), "actor_ref": ident,
        "action": ident, "resource_ref": ident, "occurred_at": timestamp, "recorded_at": timestamp,
        "correlation_id": ident, "causation_id": nullable(ident), "outcome": enum("ACCEPTED", "REJECTED", "FAILED"),
        "reason_code": ident, "context_refs": array(ref("EvidenceRef"), 50)})
    schemas["SystemStatus"] = obj({"api_version": {"const": "v1"}, "build_sha": sha,
        "mode": {"const": "SIMULATED_ONLY"}, "process_live": {"type": "boolean"}, "service_ready": {"type": "boolean"},
        "dependencies": array(obj({"name": ident, "state": enum("UP", "DOWN", "UNKNOWN"), "reason_code": ident}), 20),
        "workload_policy_ref": ref("EvidenceRef"), "sampled_at": timestamp})
    schemas["LoginRequest"] = obj({"username": {"type": "string", "minLength": 1, "maxLength": 128},
        "password": {"type": "string", "minLength": 1, "maxLength": 1024, "writeOnly": True}})
    schemas["OperatorSession"] = obj({"operator_id": ident, "expires_at": timestamp,
        "permissions": array(enum("OPERATOR_READ", "OPERATOR_WRITE"), 2)})
    schemas["CsrfToken"] = obj({"request_token": {"type": "string", "minLength": 32, "maxLength": 512}})
    for singular in ("DatasetManifest", "StrategyDefinition", "ResearchRun", "ReconciliationCase", "AuditEvent"):
        schemas[singular + "Page"] = obj({"items": array(ref(singular)),
            "next_cursor": nullable({"type": "string", "minLength": 1, "maxLength": 4096}), "snapshot_ref": ref("EvidenceRef")})

    params = {
        "Id": {"name": "id", "in": "path", "required": True, "schema": ident},
        "IdempotencyKey": {"name": "Idempotency-Key", "in": "header", "required": True, "schema": ident},
        "IfMatch": {"name": "If-Match", "in": "header", "required": True,
                    "schema": {"type": "string", "pattern": '^"[1-9][0-9]*"$'}, "description": 'Quoted positive revision, e.g. "3"; wildcard forbidden.'},
        "Limit": {"name": "limit", "in": "query", "schema": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 100}},
        "Cursor": {"name": "cursor", "in": "query", "schema": {"type": "string", "minLength": 1, "maxLength": 4096}},
        "Csrf": {"name": "X-CSRF-Token", "in": "header", "required": True, "schema": {"type": "string", "minLength": 32, "maxLength": 512}},
    }
    error_status = {"400": "INVALID_INPUT", "401": "UNAUTHENTICATED", "403": "FORBIDDEN", "404": "NOT_FOUND",
        "409": "REVISION_CONFLICT / IDEMPOTENCY_CONFLICT / READINESS_BLOCKED", "422": "INVALID_INPUT / UNQUALIFIED_DATA / WORKLOAD_LIMIT_EXCEEDED",
        "413": "WORKLOAD_LIMIT_EXCEEDED (body/file bytes)",
        "429": "RATE_LIMITED", "500": "INTERNAL_ERROR", "503": "DEPENDENCY_UNAVAILABLE"}
    responses = {status: {"description": desc, "content": {"application/json": {"schema": ref("Error")}}}
                 for status, desc in error_status.items()}
    paths = {}

    def endpoint(path, method, name, response, request=None, revision=False, page=False, transaction="READ_ONLY_SNAPSHOT", async_=False):
        mutation = method == "post"
        parameters = ([{"$ref": "#/components/parameters/Id"}] if "{id}" in path else [])
        if page:
            parameters += [{"$ref": "#/components/parameters/" + p} for p in ("Limit", "Cursor")]
        if mutation:
            parameters += [{"$ref": "#/components/parameters/IdempotencyKey"}]
        if revision:
            parameters += [{"$ref": "#/components/parameters/IfMatch"}]
        code = "202" if async_ else ("201" if mutation else "200")
        operation = {"operationId": name, "summary": name, "parameters": parameters,
            "responses": {code: {"description": "Accepted command receipt; poll referenced operation." if async_ else "Validated projection.",
                "content": {"application/json": {"schema": ref(response)}}},
                **{s: {"$ref": "#/components/responses/" + s} for s in error_status}},
            "x-contract": {"owner": "PYTHON", "permission": "OPERATOR_WRITE" if mutation else "OPERATOR_READ",
                "authority": "SIMULATED_ONLY; reject broker/LIVE resources and unregistered input references",
                "transaction": transaction, "async": async_,
                "idempotency": "actor + operationId + resource id (collection for create); durable original receipt replay before revision check" if mutation else "READ_ONLY",
                "expected_revision": "REQUIRED_CAS" if revision else "NOT_APPLICABLE_CREATE_OR_READ",
                "retry": "On lost response repeat identical key/payload/If-Match; never new key. 503/429 use bounded backoff." if mutation else "Safe bounded retry; cursor snapshot cannot be silently replaced.",
                "cancellation": "Explicit operation cancel or session STOP only; disconnect is not cancellation.",
                "pagination": "Snapshot-bound opaque cursor, default 100/max 1000; fixed identity sort." if page else "Bounded non-paginated projection.",
                "audit": "Atomic command acceptance/rejection receipts; redact payload secrets." if mutation else "Access telemetry with actor/correlation; not economic evidence."}}
        if request:
            operation["requestBody"] = {"required": True, "content": {"application/json": {"schema": ref(request)}}}
        paths.setdefault(path, {})[method] = operation

    endpoint("/api/v1/datasets", "get", "listDatasets", "DatasetManifestPage", page=True)
    endpoint("/api/v1/strategies", "get", "listStrategies", "StrategyDefinitionPage", page=True)
    endpoint("/api/v1/research-runs", "post", "createResearchRun", "CommandReceipt", "ResearchRunRequest", transaction="ATOMIC_RUN_COMMAND_OPERATION", async_=True)
    endpoint("/api/v1/research-runs", "get", "listResearchRuns", "ResearchRunPage", page=True)
    endpoint("/api/v1/operations/{id}", "get", "getOperation", "Operation")
    endpoint("/api/v1/operations/{id}/cancel", "post", "cancelOperation", "CommandReceipt", "CancelRequest", revision=True, transaction="COMMAND_RECEIPT_AND_OPERATION_CAS", async_=True)
    endpoint("/api/v1/research-runs/{id}/results", "get", "getResearchResults", "ResearchResults")
    endpoint("/api/v1/simulation-sessions", "post", "createSimulation", "CommandReceipt", "SimulationRequest", transaction="RESERVATION_RECEIPT_OPERATION_THEN_FENCED_ATOMIC_GENESIS_PUBLICATION", async_=True)
    endpoint("/api/v1/simulation-sessions/{id}", "get", "getSimulation", "SimulationSession")
    endpoint("/api/v1/simulation-sessions/{id}/commands", "post", "commandSimulation", "CommandReceipt", "SimulationCommand", revision=True, transaction="COMMAND_SESSION_CAS_AND_OPERATION", async_=True)
    endpoint("/api/v1/accounts/{id}/state", "get", "getAccountState", "AccountState")
    endpoint("/api/v1/reconciliation-cases", "get", "listReconciliationCases", "ReconciliationCasePage", page=True)
    endpoint("/api/v1/audit", "get", "listAudit", "AuditEventPage", page=True)
    endpoint("/api/v1/system/status", "get", "getSystemStatus", "SystemStatus")
    endpoint("/api/v1/commands/{id}", "get", "getCommandReceipt", "CommandReceipt")
    endpoint("/api/v1/dataset-imports", "post", "importDataset", "CommandReceipt", "DatasetImportRequest", transaction="STAGED_FILE_AND_IMPORT_COMMAND_OPERATION", async_=True)
    import_body = paths["/api/v1/dataset-imports"]["post"]["requestBody"]
    import_body["content"]["multipart/form-data"] = import_body["content"].pop("application/json")
    import_body["content"]["multipart/form-data"]["encoding"] = {"metadata": {"contentType": "application/json"}, "file": {"contentType": "text/csv"}}
    endpoint("/api/v1/strategy-configs", "post", "createStrategyConfig", "CommandReceipt", "StrategyConfigRequest", transaction="IMMUTABLE_CONFIG_AND_COMMAND_RECEIPT")
    endpoint("/api/v1/strategy-configs/{id}", "get", "getStrategyConfig", "StrategyConfigVersion")
    endpoint("/api/v1/configuration-catalog", "get", "getConfigurationCatalog", "ConfigurationCatalog")
    endpoint("/api/v1/reconciliation-cases/{id}/resolve", "post", "resolveReconciliationCase", "CommandReceipt", "ResolveCaseRequest", revision=True, transaction="ACCEPTED_CASE_VERSION_APPEND_AND_RECEIPT")
    endpoint("/api/v1/artifacts/{id}/rows", "get", "getArtifactRows", "ArtifactRows", page=True)
    endpoint("/api/v1/artifacts/{id}/download", "get", "downloadArtifact", "ArtifactManifest")
    paths["/api/v1/artifacts/{id}/download"]["get"]["responses"]["200"] = {
        "description": "Published bytes, authorized by artifact identity; attachment filename server-derived; no path input or Range support.",
        "headers": {"ETag": {"schema": {"type": "string"}, "description": "Quoted SHA256 byte digest"},
                    "Content-Disposition": {"schema": {"type": "string"}},
                    "X-Content-Type-Options": {"schema": {"const": "nosniff"}}},
        "content": {"application/octet-stream": {"schema": {"type": "string", "format": "binary"}}}}
    base = {"openapi": "3.1.0", "info": {"title": "V1 internal Python API — P00 candidate", "version": "1.0.0-candidate"},
        "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",
        "x-status": "CANDIDATE_NOT_ACCEPTED_NOT_IMPLEMENTED", "servers": [{"url": "https://python.internal"}],
        "security": [{"ServiceToken": []}], "paths": paths,
        "components": {"schemas": schemas, "parameters": params, "responses": responses,
            "securitySchemes": {"ServiceToken": {"type": "http", "scheme": "bearer", "description": "Private service identity; actor context accepted only from authenticated BFF."}}}}
    bff = deepcopy(base)
    bff["info"]["title"] = "V1 browser BFF API — P00 candidate"
    bff["servers"] = [{"url": "https://localhost:7443"}]
    bff["security"] = [{"OperatorCookie": []}]
    bff["components"]["securitySchemes"] = {"OperatorCookie": {"type": "apiKey", "in": "cookie", "name": "fts.session",
        "description": "ASP.NET Identity secure HttpOnly same-site cookie; no browser bearer service credentials."}}
    for path in bff["paths"].values():
        for method, operation in path.items():
            operation["x-contract"]["owner"] = "APPLICATION_MEDIATION_PYTHON_DOMAIN_AUTHORITY"
            if method == "post":
                operation["parameters"].append({"$ref": "#/components/parameters/Csrf"})
    for path, method, operation_id, response_name, anonymous in (
        ("/auth/csrf", "get", "getCsrf", "CsrfToken", True),
        ("/auth/login", "post", "loginOperator", "OperatorSession", True),
        ("/auth/session", "get", "getOperatorSession", "OperatorSession", False),
        ("/auth/logout", "post", "logoutOperator", None, False)):
        code = "204" if response_name is None else "200"
        response = {"description": "Authentication outcome; Cache-Control no-store; cookies managed by ASP.NET Identity."}
        if response_name:
            response["content"] = {"application/json": {"schema": ref(response_name)}}
        operation = {"operationId": operation_id, "summary": operation_id,
            "security": [] if anonymous else [{"OperatorCookie": []}],
            "parameters": [{"$ref": "#/components/parameters/Csrf"}] if method == "post" else [],
            "responses": {code: response, **{s: {"$ref": "#/components/responses/" + s} for s in error_status}},
            "x-contract": {"owner": "APPLICATION_IDENTITY", "transaction": "IDENTITY_SESSION_STORE",
                "permission": "ANONYMOUS_SAME_ORIGIN" if anonymous else "AUTHENTICATED_OPERATOR",
                "authority": "IDENTITY_ONLY_NOT_TRADING_PERMISSION", "idempotency": "NO_DOMAIN_COMMAND_RECEIPT_OR_PASSWORD_FINGERPRINT",
                "expected_revision": "NOT_APPLICABLE", "async": False,
                "retry": "Login is not automatically retried; logout after 401 clears local cookie state.",
                "cancellation": "Client disconnect does not imply session revocation.", "pagination": "NONE",
                "audit": "Outcome/actor/correlation only; never password, tokens or cookie values."}}
        if path == "/auth/login":
            operation["requestBody"] = {"required": True, "content": {"application/json": {"schema": ref("LoginRequest")}}}
        bff["paths"][path] = {method: operation}
    # Synthetic shape examples are not evidence that referenced domain objects exist.
    examples = {
        "Error": {"code": "READINESS_BLOCKED", "message": "Published results are not available.",
            "correlation_id": "correlation-example", "retryable": False, "operation_id": "operation-example",
            "current_revision": 1, "violations": []},
        "EvidenceRef": {"owner": "example-owner", "identity": "example-identity", "version": "v1", "sha256": "0" * 64},
        "CancelRequest": {"reason": "Operator requested cancellation."},
        "SimulationCommand": {"command": "PAUSE", "reason": "Inspect the simulation."},
    }

    def example(schema):
        if "$ref" in schema:
            name = schema["$ref"].split("/")[-1]
            return deepcopy(examples[name]) if name in examples else example(schemas[name])
        if "const" in schema:
            return schema["const"]
        if "enum" in schema:
            return schema["enum"][0]
        if "oneOf" in schema or "anyOf" in schema:
            return example(schema.get("oneOf", schema.get("anyOf"))[0])
        kind = schema.get("type")
        if kind == "object":
            return {k: example(schema["properties"][k]) for k in schema["required"]}
        if kind == "array":
            return [example(schema["items"]) for _ in range(schema.get("minItems", 0))]
        if kind == "integer":
            return schema.get("minimum", 0)
        if kind == "boolean":
            return False
        if kind == "null":
            return None
        if schema.get("format") == "date-time":
            return "2026-01-01T00:00:00Z"
        pattern = schema.get("pattern", "")
        if pattern == "^[0-9a-f]{64}$":
            return "0" * 64
        if pattern == "^[0-9a-f]{40}$":
            return "0" * 40
        if pattern.startswith("^sha256/"):
            return "sha256/" + "0" * 64
        if pattern.startswith("^partitions/"):
            return "partitions/example.parquet"
        if schema.get("maxLength") == 80:
            return "100000"
        if schema.get("minLength", 0) >= 32:
            return "synthetic-not-a-valid-token-" + "0" * 32
        return "example"

    for document in (base, bff):
        for path in document["paths"].values():
            for operation in path.values():
                if "requestBody" in operation:
                    media = next(iter(operation["requestBody"]["content"].values()))
                    media["examples"] = {"synthetic": {"summary": "Shape-only synthetic input; references require authoritative resolution.",
                                                       "value": example(media["schema"])}}
                for response in operation["responses"].values():
                    if "application/json" in response.get("content", {}):
                        media = response["content"]["application/json"]
                        media["examples"] = {"synthetic": {"summary": "Shape-only synthetic projection, not currentness evidence.",
                                                           "value": example(media["schema"])}}
    for document in (base, bff):
        receipt = document["paths"]["/api/v1/simulation-sessions"]["post"]["responses"]["202"]["content"]["application/json"]["examples"]["synthetic"]["value"]
        receipt["resource_revision_status"] = "RESERVED"
        receipt["resource_revision"] = None
    return {"python.openapi.v1.json": base, "bff.openapi.v1.json": bff}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只驗證 generated contracts 無 drift，不寫檔")
    args = parser.parse_args()
    for name, value in build().items():
        rendered = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        target = OUT / name
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != rendered:
                raise SystemExit(f"GENERATED_CONTRACT_DRIFT: {name}")
        else:
            OUT.mkdir(parents=True, exist_ok=True)
            target.write_text(rendered, encoding="utf-8")
    print("P00_CONTRACT_GENERATION_CHECK_PASS" if args.check else "P00_CANDIDATE_CONTRACTS_GENERATED")


if __name__ == "__main__":
    main()
