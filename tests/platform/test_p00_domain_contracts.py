"""Domain DTO 與既有 source binding 的負例；不是交易 runtime 驗收。"""

import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess

import pytest
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[2]
SPEC = json.loads((ROOT / "docs/architecture/contracts/python.openapi.v1.json").read_text(encoding="utf-8"))
EVIDENCE = {"owner": "fixture", "identity": "fixture-id", "version": "v1", "sha256": "0" * 64}


def validate(name, value):
    Draft202012Validator({"$ref": f"#/components/schemas/{name}", "components": SPEC["components"]}).validate(value)


def signal():
    return {"schema_version": "signal.v1", "signal_id": "signal-1", "strategy_instance_id": "instance-1",
        "strategy_version": "ema-v2", "config_version": "config-v1", "instrument_id": 1, "contract_id": 1,
        "observation_revision_id": "mor1_" + "0" * 64, "desired_net_quantity": 0,
        "previous_virtual_position_ref": EVIDENCE, "state_snapshot_ref": EVIDENCE, "correlation_id": "corr-1"}


def risk():
    return {"schema_version": "risk_decision.v1", "risk_decision_id": "risk-1", "decision_id": "decision-1",
        "account_revision": 1, "capital_revision": 1, "policy_ref": EVIDENCE, "margin_ref": EVIDENCE,
        "proposed_net_quantity": 2, "constraint_evidence": [EVIDENCE], "reason_codes": ["LIMIT_EXCEEDED"],
        "outcome": "REJECT", "approved_net_quantity": None}


def test_rejection_is_no_permission_not_flat_target():
    value = risk()
    validate("RiskDecision", value)
    value["approved_net_quantity"] = 0
    with pytest.raises(ValidationError):
        validate("RiskDecision", value)
    value["outcome"] = "REDUCE"
    validate("RiskDecision", value)
    value["approved_net_quantity"] = None
    with pytest.raises(ValidationError):
        validate("RiskDecision", value)


def test_virtual_flat_requires_positive_provenance_not_missing_previous_state():
    value = signal()
    validate("Signal", value)
    del value["previous_virtual_position_ref"]
    with pytest.raises(ValidationError):
        validate("Signal", value)


@pytest.mark.parametrize("revision", ["last-bar", "mor1_" + "a" * 63, "mor1_" + "A" * 64, "2026-01-01"])
def test_observation_revision_cannot_be_alias_or_timestamp(revision):
    value = signal()
    value["observation_revision_id"] = revision
    with pytest.raises(ValidationError):
        validate("Signal", value)


def test_implementation_version_does_not_require_git_sha():
    value = {"strategy_id": "ema", "implementation_revision": "ema-v2", "config_schema_ref": EVIDENCE,
             "supported_timeframes": ["1m"], "supported_modes": ["BACKTEST", "SIMULATED"]}
    validate("StrategyDefinition", value)
    value["implementation_revision"] = ""
    with pytest.raises(ValidationError):
        validate("StrategyDefinition", value)


def test_staged_exit_keeps_ultimate_target_distinct():
    value = {"schema_version": "decision.v1", "decision_id": "d1", "account_id": "a1", "instrument_id": 1,
        "contract_id": 1, "account_revision": 1, "cohort_id": "c1", "policy_ref": EVIDENCE,
        "recovery_cut_ref": EVIDENCE, "observation_revision_id": "mor1_" + "0" * 64,
        "signal_ids": ["s1"], "expected_net_quantity": 1, "desired_net_quantity": -1,
        "proposed_net_quantity": 0, "action": "EXIT",
        "attributions": [{"strategy_instance_id": "i1", "selected_net_quantity": -1, "signal_id": "s1"}],
        "excluded_signals": [], "correlation_id": "corr1"}
    validate("Decision", value)
    del value["desired_net_quantity"]
    with pytest.raises(ValidationError):
        validate("Decision", value)


def test_bound_accepted_source_class_and_blobs_still_exist():
    bindings = json.loads((ROOT / "docs/architecture/contracts/domain_source_bindings.v1.json").read_text(encoding="utf-8"))
    for binding in bindings["bindings"]:
        spec = binding["baseline_sha"] + ":" + binding["source_path"]
        raw = subprocess.check_output(["git", "--no-replace-objects", "-C", str(ROOT), "show", spec])
        blob = subprocess.check_output(["git", "--no-replace-objects", "-C", str(ROOT), "rev-parse", spec], text=True).strip()
        assert blob == binding["git_blob"]
        assert hashlib.sha256(raw).hexdigest() == binding["sha256"]
        assert any(isinstance(node, ast.ClassDef) and node.name == binding["source_class"]
                   for node in ast.walk(ast.parse(raw.decode("utf-8-sig"))))


def test_existing_priority_policy_is_order_independent_and_rejects_opposite_tie():
    from itertools import permutations
    from types import SimpleNamespace
    from backtest.models import Direction
    from backtest.strategy_priority_policy import PriorityStrategyConflictPolicy
    policy = PriorityStrategyConflictPolicy()
    inputs = [SimpleNamespace(priority=1, direction=Direction.LONG),
              SimpleNamespace(priority=2, direction=Direction.SHORT)]
    for ordering in permutations(inputs):
        assert policy.resolve(ordering) == Direction.SHORT
    inputs[0].priority = 2
    for ordering in permutations(inputs):
        with pytest.raises(ValueError, match="equal priority conflict"):
            policy.resolve(ordering)


def test_domain_envelope_cannot_change_semantic_owner_or_omit_provenance():
    value = {"schema_version": "trading_evidence.v1", "evidence_id": "signal-1", "owner": "E",
        "actor_ref": "simulation-worker", "recorded_at": "2026-01-01T00:00:00Z", "correlation_id": "corr-1",
        "causation_id": None, "payload_hash": "0" * 64, "payload": signal()}
    validate("TradingEvidenceEnvelope", value)
    value["owner"] = "G"
    with pytest.raises(ValidationError):
        validate("TradingEvidenceEnvelope", value)
    value["owner"] = "E"
    del value["payload_hash"]
    with pytest.raises(ValidationError):
        validate("TradingEvidenceEnvelope", value)
