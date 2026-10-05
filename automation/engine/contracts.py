"""Automation governance YAML 的唯讀 machine contract。

本模組只描述既有 frozen records 的資料形狀，供 loader 與後續 shadow
automation 使用；它不判斷授權是否有效，也不改變任何 governance state。
"""

from __future__ import annotations

import math
from types import MappingProxyType
from typing import Literal, Mapping, TypeAlias

from pydantic import BaseModel, ConfigDict, model_validator


FrozenSection: TypeAlias = Mapping[str, object]


def _normalize_yaml_sequences(value: object) -> object:
    """只正規化 YAML collection，不允許 scalar coercion。"""

    if isinstance(value, Mapping):
        return {key: _normalize_yaml_sequences(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return tuple(_normalize_yaml_sequences(item) for item in value)
    return value


def _freeze_yaml_value(value: object) -> object:
    """將 safe YAML 的 JSON-like 結構遞迴轉為唯讀值。"""

    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("YAML contract does not allow non-finite numbers")
        return value
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("YAML contract mapping keys must be strings")
        return MappingProxyType(
            {key: _freeze_yaml_value(item) for key, item in value.items()}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_yaml_value(item) for item in value)
    raise ValueError(f"unsupported YAML contract value: {type(value).__name__}")


class AutomationContract(BaseModel):
    """所有 machine contract 的共同 fail-closed 與深層唯讀邊界。"""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    @model_validator(mode="before")
    @classmethod
    def _accept_yaml_sequences(cls, value: object) -> object:
        return _normalize_yaml_sequences(value)

    @model_validator(mode="after")
    def _make_sections_read_only(self) -> "AutomationContract":
        for field_name in type(self).model_fields:
            object.__setattr__(
                self,
                field_name,
                _freeze_yaml_value(getattr(self, field_name)),
            )
        return self


class MasterManifest(AutomationContract):
    """Development Automation master manifest 的 frozen top-level contract。"""

    schema_version: Literal["automation.master_manifest.v1"]
    manifest_id: str
    manifest_version: str
    master_architecture_version: str
    status: str
    materialization_baseline_sha: str
    compiled_program: FrozenSection
    compiled_authorization_candidate: FrozenSection
    superseded_authorization_candidates: tuple[FrozenSection, ...]
    quota_policy_compatibility_rf: FrozenSection
    freeze: FrozenSection
    hash_integrity: FrozenSection
    canonical_current_state: FrozenSection
    governance_document: FrozenSection
    agent_reentry: FrozenSection
    policies: FrozenSection
    negative_assertions: FrozenSection
    activation: FrozenSection


class AuthorizationRecord(AutomationContract):
    """Exact-bound、single-use authorization record；模型本身不授予執行權。"""

    schema_version: Literal["automation.authorization.v1"]
    authorization_id: str
    authorization_revision: str
    document_status: str
    authorization_state: str
    source_candidate_head_sha: str
    decision_evidence: FrozenSection
    exact_binding: FrozenSection
    program_binding: FrozenSection
    package_binding: FrozenSection
    execution_policy: FrozenSection
    side_effect_envelope: FrozenSection
    quota_gate: FrozenSection
    telemetry_gate: FrozenSection
    decision: FrozenSection
    single_use_execution: FrozenSection


class WorkPackageRecord(AutomationContract):
    """單一 bounded work package plan；不把 PLANNED 狀態提升為 AUTHORIZED。"""

    schema_version: Literal["automation.work_package_plan.v1"]
    work_package_id: str
    work_package_revision: str
    status: str
    program_id: str
    planning_baseline_sha: str
    wave: str
    title: str
    risk: str
    depends_on: tuple[str, ...]
    purpose: str
    authorization: FrozenSection
    side_effect_envelope: FrozenSection
    planned_write_scope: tuple[str, ...]
    protected_scope: tuple[str, ...]
    acceptance_tests: tuple[str, ...]
    cost_forecast: FrozenSection
    telemetry: FrozenSection
    git_policy: FrozenSection
    review_barrier: str


class AuthorizationLifecyclePolicy(AutomationContract):
    """Authorization lifecycle policy 的 frozen record。"""

    schema_version: Literal["automation.authorization_lifecycle.v1"]
    policy_id: str
    policy_version: str
    status: str
    authority: FrozenSection
    states: tuple[str, ...]
    exact_binding: FrozenSection
    single_use_dispatch: FrozenSection
    restart_semantics: FrozenSection
    fail_closed: FrozenSection


class QuotaAdmissionPolicy(AutomationContract):
    """Quota admission v1.1 record；只載入證據規則，不執行 admission。"""

    schema_version: Literal["automation.quota_admission_policy.v1_1"]
    policy_id: str
    policy_version: str
    status: str
    active: bool
    materialization: FrozenSection
    authority: FrozenSection
    admission: FrozenSection
    forecast: FrozenSection
    source_separation: FrozenSection
    forecast_semantics: FrozenSection
    chatgpt_plan_normalized_fallback: FrozenSection
    wait: FrozenSection
    alternate_package: FrozenSection
    executor_profile: FrozenSection
    api_channel: FrozenSection
    optimization: FrozenSection
    hard_invariants: tuple[str, ...]


class DevelopmentStateMachinePolicy(AutomationContract):
    """Automation 各正交狀態軸與 transition invariant 的 frozen record。"""

    schema_version: Literal["automation.development_state_machine.v1"]
    policy_id: str
    policy_version: str
    status: str
    axes: FrozenSection
    required_invariants: tuple[str, ...]
    quota_wait_reentry: FrozenSection


class DevelopmentEntryProtocol(AutomationContract):
    """Repository-first unified re-entry protocol 的 frozen record。"""

    schema_version: Literal["automation.development_entry_protocol.v1"]
    policy_id: str
    policy_version: str
    status: str
    entry_surface: FrozenSection
    bootstrap: FrozenSection
    routing_priority: tuple[str, ...]
    user_intent_reentry: FrozenSection
    required_run_identity: tuple[str, ...]
    deduplication: FrozenSection
    authority_rules: FrozenSection
    scheduled_events: FrozenSection


class ImplementationProgram(AutomationContract):
    """已接受之 implementation planning program；不等同 package authorization。"""

    schema_version: Literal["automation.implementation_program.v1"]
    program_id: str
    program_revision: str
    status: str
    compiled_from_freeze_head: str
    frozen_master_manifest_sha256: str
    master_architecture_version: str
    authority: FrozenSection
    implementation_strategy: FrozenSection
    near_horizon_exact_packages: tuple[FrozenSection, ...]
    dag: tuple[str, ...]
    waves: FrozenSection
    deferred_milestones: tuple[FrozenSection, ...]
    hard_stops: tuple[str, ...]
    authorization_compilation: FrozenSection


CONTRACT_BY_SCHEMA: Mapping[str, type[AutomationContract]] = MappingProxyType(
    {
        "automation.master_manifest.v1": MasterManifest,
        "automation.authorization.v1": AuthorizationRecord,
        "automation.work_package_plan.v1": WorkPackageRecord,
        "automation.authorization_lifecycle.v1": AuthorizationLifecyclePolicy,
        "automation.quota_admission_policy.v1_1": QuotaAdmissionPolicy,
        "automation.development_state_machine.v1": DevelopmentStateMachinePolicy,
        "automation.development_entry_protocol.v1": DevelopmentEntryProtocol,
        "automation.implementation_program.v1": ImplementationProgram,
    }
)


__all__ = [
    "AuthorizationLifecyclePolicy",
    "AuthorizationRecord",
    "AutomationContract",
    "CONTRACT_BY_SCHEMA",
    "DevelopmentEntryProtocol",
    "DevelopmentStateMachinePolicy",
    "ImplementationProgram",
    "MasterManifest",
    "QuotaAdmissionPolicy",
    "WorkPackageRecord",
]
