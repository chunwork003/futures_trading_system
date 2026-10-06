"""V2 純證據評估：不讀 provider、不 invoke、不建立或改寫授權。

輸入由 control plane 以 exact repository/head/lineage 證據組裝；結果僅為
下一個治理步驟建議。候選 policy 不因本模組存在而啟用。
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal
from pydantic import model_validator
from automation.engine.contracts import AutomationContract, FrozenSection


class ProviderEvidence(AutomationContract):
    ordinary_usage_allowed: bool
    hard_block: bool
    rate_limit_denied: bool
    spend_control_denied: bool
    raw: FrozenSection


class DemandForecast(AutomationContract):
    p50: int
    p75: int
    p90: int
    token_dimensions: FrozenSection

    @model_validator(mode="after")
    def ordered_bands(self):
        if not 0 <= self.p50 <= self.p75 <= self.p90:
            raise ValueError("invalid forecast bands")
        return self


IDENTITY_DIMENSIONS = ("provider", "account", "workspace", "limit_id", "window_type",
                       "model", "executor_profile", "provider_client_policy_version")
TOKEN_DIMENSIONS = ("input_tokens", "cached_input_tokens", "uncached_input_tokens",
                    "output_tokens", "reasoning_output_tokens", "total_tokens")


class CalibrationSample(AutomationContract):
    execution_id: str
    measurement_type: Literal["EXACT"]
    identity: FrozenSection
    token_features: FrozenSection
    provider_before: FrozenSection
    provider_after: FrozenSection
    exact_binding_verified: bool
    clean_attribution: bool
    reset_compatible: bool
    competing_consumer: bool


def qualified_samples(samples: tuple[CalibrationSample, ...], identity: FrozenSection) -> bool:
    """樣本數不是 confidence 升級；每個 identity、歸因與 reset 證據皆必須合格。"""
    if len(samples) < 3 or len({s.execution_id for s in samples}) != len(samples):
        return False
    if any(not isinstance(identity.get(k), str) or not identity[k].strip() for k in IDENTITY_DIMENSIONS):
        return False
    for sample in samples:
        if (not sample.execution_id or not sample.exact_binding_verified or not sample.clean_attribution
                or not sample.reset_compatible or sample.competing_consumer):
            return False
        if any(sample.identity.get(k) != identity[k] for k in IDENTITY_DIMENSIONS):
            return False
        if any(type(sample.token_features.get(k)) is not int or sample.token_features[k] < 0
               for k in TOKEN_DIMENSIONS):
            return False
        f = sample.token_features
        if (f["cached_input_tokens"] + f["uncached_input_tokens"] != f["input_tokens"]
                or f["reasoning_output_tokens"] > f["output_tokens"]
                or f["total_tokens"] != f["input_tokens"] + f["output_tokens"]):
            return False
        if not sample.provider_before or not sample.provider_after:
            return False
        # reset/百分比相符不足以證明 window identity；必要事實不能由 identity 補造。
        for key in ("provider", "limit_id", "window_type"):
            if any(window.get(key) != identity[key]
                   for window in (sample.provider_before, sample.provider_after)):
                return False
        for key in IDENTITY_DIMENSIONS:
            if key in sample.provider_before or key in sample.provider_after:
                if any(window.get(key) != identity[key]
                       for window in (sample.provider_before, sample.provider_after)):
                    return False
        duration = "window_duration_mins"
        if duration in identity or duration in sample.provider_before or duration in sample.provider_after:
            before_duration = sample.provider_before.get(duration)
            after_duration = sample.provider_after.get(duration)
            if (type(before_duration) is not int or before_duration <= 0
                    or type(after_duration) is not int or before_duration != after_duration
                    or (duration in identity and before_duration != identity[duration])):
                return False
        if (sample.provider_before.get("resets_at") is None
                or sample.provider_before.get("resets_at") != sample.provider_after.get("resets_at")):
            return False
        before, after = sample.provider_before.get("used_percent"), sample.provider_after.get("used_percent")
        if (type(before) not in (int, float) or type(after) not in (int, float)
                or not 0 <= before <= after <= 100):
            return False
    return True


class CapacityEstimate(AutomationContract):
    measurement_type: Literal["PROVISIONAL_ESTIMATE", "CALIBRATED_ESTIMATE"]
    identity: FrozenSection
    available_tokens_lower: int | None
    available_tokens_upper: int | None
    feature_method: str
    uncertainty: str
    samples: tuple[CalibrationSample, ...]
    qualification_reviewed: bool

    @model_validator(mode="after")
    def validate_estimate(self):
        lower, upper = self.available_tokens_lower, self.available_tokens_upper
        if (lower is None) != (upper is None) or (lower is not None and not 0 <= lower <= upper):
            raise ValueError("invalid capacity interval")
        if not self.feature_method or not self.uncertainty:
            raise ValueError("capacity method/uncertainty required")
        if self.measurement_type == "CALIBRATED_ESTIMATE" and (
                not self.qualification_reviewed or not qualified_samples(self.samples, self.identity)):
            raise ValueError("unqualified capacity calibration")
        return self


@dataclass(frozen=True)
class GateResult:
    route: str
    reason: str
    execution_allowed: bool = False
    authority_created: bool = False
    forecast_capacity_review_required: bool = False


def provider_gate(provider: ProviderEvidence) -> GateResult:
    available = (provider.ordinary_usage_allowed and not provider.hard_block
                 and not provider.rate_limit_denied and not provider.spend_control_denied)
    return GateResult("PROVIDER_AVAILABLE" if available else "WAIT_PROVIDER_AVAILABLE",
                      "PROVIDER_REPORTED_AVAILABILITY" if available else "PROVIDER_ACTUAL_DENIAL")


def cost_gate(forecast: DemandForecast, capacity: CapacityEstimate | None, *,
              exact_authorized: bool, manual: bool, low_risk: bool) -> GateResult:
    """需求與 capacity 分軸；缺 calibration 不捏造數值或 percent/token 換算。"""
    if not exact_authorized:
        return GateResult("STOP_TO_WORK", "EXACT_AUTHORITY_REQUIRED")
    if capacity is None or capacity.measurement_type == "PROVISIONAL_ESTIMATE":
        if manual and low_risk:
            return GateResult("ALLOW_WITH_WATCH", "PROVISIONAL_EXPLICIT_MANUAL_LOW_RISK")
        return GateResult("WORK_CAPACITY_REVIEW", "QUALIFIED_CAPACITY_REQUIRED")
    if capacity.available_tokens_lower is None or forecast.p90 > capacity.available_tokens_lower:
        return GateResult("WORK_CAPACITY_REVIEW", "FORECAST_CAPACITY_MISS", forecast_capacity_review_required=True)
    return GateResult("COST_FIT", "QUALIFIED_ESTIMATE_WITH_UNCERTAINTY")


def evaluate_admission(provider: ProviderEvidence, forecast: DemandForecast,
                       capacity: CapacityEstimate | None, *, exact_authorized: bool,
                       manual: bool, low_risk: bool) -> GateResult:
    """Provider 實際拒絕先於 cost；fit 仍不等於 executor invocation authority。"""
    availability = provider_gate(provider)
    if availability.route != "PROVIDER_AVAILABLE":
        return availability
    return cost_gate(forecast, capacity, exact_authorized=exact_authorized, manual=manual, low_risk=low_risk)


class ExecutionLineage(AutomationContract):
    work_order_id: str
    execution_id: str
    authorization_id: str
    reservation_id: str
    dispatch_id: str
    branch: str
    scope_digest: str
    architecture_policy_identity: str
    correction_budget: int
    delta_sha: str
    completed_tests: tuple[str, ...]
    telemetry: FrozenSection


class ResumeEvidence(AutomationContract):
    original: ExecutionLineage
    current: ExecutionLineage
    authorization_state: Literal["CONSUMED", "REVOKED", "SUPERSEDED", "AUTHORIZED", "RESERVED"]
    reservation_created: bool
    dispatch_committed: bool
    executor_invoked: bool
    invocation_evidence_verified: bool
    head_compatible: bool
    scope_compatible: bool
    architecture_policy_compatible: bool
    writer_owner: str
    writer_state: Literal["HELD", "REACQUIRED", "RELEASED"]
    writer_lineage_verified: bool
    competing_writer: bool
    projection_phase: Literal["CURRENT_LIFECYCLE_PROJECTION", "HISTORICAL_PHASE_SNAPSHOT"]
    projection: FrozenSection
    provider: ProviderEvidence


@dataclass(frozen=True)
class ExecutionCheckpoint:
    lineage: ExecutionLineage
    state: str
    provider_pause_count: int = 0
    resume_count: int = 0
    forecast_capacity_review_required: bool = False


def pause_provider_limit(checkpoint: ExecutionCheckpoint, provider: ProviderEvidence) -> ExecutionCheckpoint:
    """純 checkpoint proposal；保存同一 lineage/budget/tests，不寫 lock 或消耗 correction。"""
    if checkpoint.state != "RUNNING" or provider_gate(provider).route == "PROVIDER_AVAILABLE":
        raise ValueError("running provider denial evidence required")
    return replace(checkpoint, state="PAUSED_PROVIDER_LIMIT",
                   provider_pause_count=checkpoint.provider_pause_count + 1,
                   forecast_capacity_review_required=True)


def provider_recovery_wake(checkpoint: ExecutionCheckpoint) -> ExecutionCheckpoint:
    if checkpoint.state != "PAUSED_PROVIDER_LIMIT":
        raise ValueError("paused checkpoint required")
    return replace(checkpoint, state="RESUME_PENDING_REVALIDATION")


def evaluate_resume(checkpoint: ExecutionCheckpoint, evidence: ResumeEvidence) -> GateResult:
    """Resume 與 consumed redispatch 不同；缺首次 invocation 證據永不補造。"""
    if checkpoint.state != "RESUME_PENDING_REVALIDATION":
        return GateResult("STOP_TO_WORK", "FRESH_RESUME_REVALIDATION_REQUIRED")
    projection = evidence.projection
    if evidence.projection_phase != "CURRENT_LIFECYCLE_PROJECTION" or any(
        type(projection.get(k)) is not type(v) or projection.get(k) != v for k, v in {
            "execution_id": evidence.current.execution_id,
            "authorization_state": evidence.authorization_state,
            "reservation_created": evidence.reservation_created,
            "dispatch_committed": evidence.dispatch_committed,
            "executor_invoked": evidence.executor_invoked,
            "writer_owner": evidence.writer_owner,
            "writer_state": evidence.writer_state,
        }.items()
    ):
        return GateResult("RECONCILIATION_REQUIRED", "HISTORICAL_PHASE_SNAPSHOT_NOT_CURRENT_OR_CONTRADICTION")
    if evidence.original != checkpoint.lineage or evidence.current != evidence.original:
        return GateResult("STOP_TO_WORK", "EXECUTION_LINEAGE_CHANGED")
    if any(not getattr(evidence.current, k) for k in (
            "work_order_id", "execution_id", "authorization_id", "reservation_id", "dispatch_id",
            "branch", "scope_digest", "architecture_policy_identity", "delta_sha")):
        return GateResult("STOP_TO_WORK", "MISSING_LINEAGE")
    if evidence.authorization_state != "CONSUMED" or not all((
            evidence.reservation_created, evidence.dispatch_committed, evidence.executor_invoked,
            evidence.invocation_evidence_verified, evidence.head_compatible, evidence.scope_compatible,
            evidence.architecture_policy_compatible, evidence.writer_lineage_verified)):
        return GateResult("STOP_TO_WORK", "RESUME_BINDING_INVALID_NO_REDISPATCH")
    if (evidence.writer_owner != evidence.current.execution_id or evidence.competing_writer
            or evidence.writer_state not in ("HELD", "REACQUIRED")):
        return GateResult("STOP_TO_WORK", "WRITER_CONFLICT")
    if provider_gate(evidence.provider).route != "PROVIDER_AVAILABLE":
        return GateResult("WAIT_PROVIDER_AVAILABLE", "PROVIDER_ACTUAL_DENIAL", forecast_capacity_review_required=True)
    return GateResult("RESUME_SAME_EXECUTION", "EXACT_ALREADY_INVOKED_REVALIDATED",
                      forecast_capacity_review_required=checkpoint.forecast_capacity_review_required)


def route_work(*, safety_block: bool, unfinished: bool, pending_review: bool,
               interrupted_completed: bool, feedback_materialized: bool,
               new_work_authorized: bool) -> GateResult:
    if safety_block:
        return GateResult("STOP_TO_WORK", "SAFETY_GOVERNANCE")
    if unfinished:
        return GateResult("REENTER_UNFINISHED_EXECUTION", "UNFINISHED_BLOCKS_NEW_DISPATCH")
    if pending_review:
        return GateResult("PENDING_REVIEW_INTEGRATION", "REVIEW_NOT_INTEGRATION_NOT_ACCEPTANCE")
    if interrupted_completed and not feedback_materialized:
        return GateResult("WORK_FORECAST_CAPACITY_REVIEW", "DURABLE_FEEDBACK_BEFORE_NEW_WORK")
    return GateResult("NEW_WORK_REVALIDATION" if new_work_authorized else "STOP_TO_WORK", "NO_AUTHORITY_CREATED")


def ivf01_route(*, active_architecture: str, governance_review_pass: bool,
                activation_materialized: bool) -> GateResult:
    if active_architecture == "1.2" and governance_review_pass and activation_materialized:
        return GateResult("ARCHITECTURE_BASELINE_CHANGED_RECOMPILE_REQUIRED", "IVF01_REV1_NEVER_REUSED")
    return GateResult("BLOCKED", "IVF01_NO_EXECUTION_NO_WAIVER")
