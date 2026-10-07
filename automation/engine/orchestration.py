"""Program V2 的純函式 orchestration control layer。"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from types import MappingProxyType
from typing import Iterable, Literal, Mapping, Sequence

WAKE_EVENT_CLASSES = frozenset({
    "MANUAL_CONTINUE", "REPOSITORY_CURRENT_CHANGED", "RESULT_AVAILABLE",
    "REVIEW_VERDICT_MATERIALIZED", "INTEGRATION_RESULT_MATERIALIZED",
    "PROVIDER_AVAILABILITY_RECOVERY", "SCHEDULED_TIMER_WAKE",
    "AUTHORIZATION_MATERIALIZED", "EXECUTION_PAUSED", "EXECUTION_COMPLETED",
})
QUEUE_STATES = frozenset({
    "OBSERVED", "BLOCKED", "WAITING", "ELIGIBLE_MANUAL",
    "ELIGIBLE_CONTROLLED_AUTO", "IN_PROGRESS", "COMPLETED", "SUPERSEDED",
})
PRIORITY_CLASSES = (
    "SAFETY_GOVERNANCE", "RESUMABLE_UNFINISHED_EXECUTION",
    "PENDING_RESULT_REVIEW_INTEGRATION", "AUTHORIZED_NEW_WORK",
)
PRIORITY_RANK = {name: index for index, name in enumerate(PRIORITY_CLASSES)}
EXECUTABLE_OR_PROGRESS_STATES = frozenset({"ELIGIBLE_MANUAL", "ELIGIBLE_CONTROLLED_AUTO", "IN_PROGRESS"})

class OrchestrationError(ValueError):
    pass
class QueueReconciliationRequired(OrchestrationError):
    pass
class StaleProjectionError(OrchestrationError):
    pass

@dataclass(frozen=True, slots=True)
class WakeEvent:
    event_class: str
    subject_id: str
    relevant_revision: str
    lifecycle_generation: int
    evidence_ref: str
    def __post_init__(self) -> None:
        if self.event_class not in WAKE_EVENT_CLASSES:
            raise OrchestrationError(f"unsupported wake event: {self.event_class}")
        if not self.subject_id or not self.relevant_revision or not self.evidence_ref:
            raise OrchestrationError("wake event identity is incomplete")
        if self.lifecycle_generation < 0:
            raise OrchestrationError("lifecycle_generation cannot be negative")
    @property
    def effect(self) -> str:
        return "WAKE_ONLY"
    @property
    def grants_authority(self) -> bool:
        return False
    @property
    def dispatches(self) -> bool:
        return False

def dedupe_key(*, subject_id: str, item_kind: str, relevant_revision: str, lifecycle_generation: int) -> str:
    if not subject_id or not item_kind or not relevant_revision:
        raise OrchestrationError("dedupe identity fields must be non-empty")
    if lifecycle_generation < 0:
        raise OrchestrationError("lifecycle_generation cannot be negative")
    payload = {
        "item_kind": item_kind,
        "lifecycle_generation": lifecycle_generation,
        "relevant_repository_revision": relevant_revision,
        "subject_identity": subject_id,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256(encoded).hexdigest()

@dataclass(frozen=True, slots=True)
class QueueItem:
    queue_item_id: str
    subject_id: str
    package_id: str | None
    work_order_id: str | None
    execution_id: str | None
    item_kind: str
    architecture_policy_identity: str
    source_revision: str
    current_relevant_revision: str
    lifecycle_generation: int
    priority_class: str
    originating_event: str
    dedupe_key: str
    queue_state: str
    blocking_reason: str | None
    authority_ref: str | None
    lifecycle_ref: str | None
    writer_lease_ref: str | None
    created_evidence: str
    updated_evidence: str
    lane_position: int | None = None
    dag_ready: bool = True
    def __post_init__(self) -> None:
        if self.priority_class not in PRIORITY_RANK:
            raise OrchestrationError(f"unsupported priority_class: {self.priority_class}")
        if self.queue_state not in QUEUE_STATES:
            raise OrchestrationError(f"unsupported queue_state: {self.queue_state}")
        if self.originating_event not in WAKE_EVENT_CLASSES:
            raise OrchestrationError(f"unsupported originating_event: {self.originating_event}")
        expected = dedupe_key(subject_id=self.subject_id, item_kind=self.item_kind,
                              relevant_revision=self.current_relevant_revision,
                              lifecycle_generation=self.lifecycle_generation)
        if self.dedupe_key != expected:
            raise OrchestrationError("queue item dedupe_key mismatch")
    @classmethod
    def build(cls, **values: object) -> "QueueItem":
        values["dedupe_key"] = dedupe_key(
            subject_id=str(values["subject_id"]), item_kind=str(values["item_kind"]),
            relevant_revision=str(values["current_relevant_revision"]),
            lifecycle_generation=int(values["lifecycle_generation"]),
        )
        return cls(**values)

def _queue_identity(item: QueueItem) -> tuple[object, ...]:
    return (item.subject_id, item.package_id, item.work_order_id, item.execution_id,
            item.item_kind, item.architecture_policy_identity, item.source_revision,
            item.current_relevant_revision, item.lifecycle_generation, item.priority_class,
            item.queue_state, item.blocking_reason, item.authority_ref, item.lifecycle_ref,
            item.writer_lease_ref, item.lane_position, item.dag_ready)

def project_queue(items: Iterable[QueueItem], *, expected_master: str | None = None,
                  actual_master: str | None = None, expected_generation: int | None = None,
                  actual_generation: int | None = None) -> tuple[QueueItem, ...]:
    if expected_master is not None and actual_master is not None and expected_master != actual_master:
        raise StaleProjectionError("master revision changed; rehydrate required")
    if expected_generation is not None and actual_generation is not None and expected_generation != actual_generation:
        raise StaleProjectionError("queue generation changed; rehydrate required")
    by_key: dict[str, QueueItem] = {}
    for item in items:
        existing = by_key.get(item.dedupe_key)
        if existing is None:
            by_key[item.dedupe_key] = item
            continue
        if _queue_identity(existing) != _queue_identity(item):
            raise QueueReconciliationRequired(f"conflicting projections for dedupe {item.dedupe_key}")
        by_key[item.dedupe_key] = min((existing, item), key=lambda c: (c.originating_event, c.queue_item_id, c.updated_evidence))
    projected = tuple(sorted(by_key.values(), key=lambda i: (
        PRIORITY_RANK[i.priority_class], i.lane_position if i.lane_position is not None else 2**31 - 1,
        i.subject_id, i.queue_item_id)))
    executable = [i for i in projected if i.queue_state in EXECUTABLE_OR_PROGRESS_STATES]
    if len(executable) > 1:
        raise QueueReconciliationRequired("more than one executable or in-progress queue item")
    return projected

CapacityState = Literal["UNKNOWN", "FIT", "INSUFFICIENT"]
DispatchMode = Literal["MANUAL", "CONTROLLED_AUTO"]
ExecutorMode = Literal["CODEX", "HUMAN_DIALOGUE"]

@dataclass(frozen=True, slots=True)
class OrchestrationSnapshot:
    fresh_master_sha: str
    active_architecture_policy_hashes: tuple[str, ...]
    current_relevant_revision: str
    lifecycle_generation: int
    safety_violation: bool = False
    authorization_revoked: bool = False
    side_effect_violation: bool = False
    missing_required_identity: bool = False
    current_contradiction: bool = False
    competing_writers: bool = False
    executable_identity_count: int = 1
    resume_requested: bool = False
    paused_execution_exists: bool = False
    paused_executor_invoked: bool = False
    paused_lineage_valid: bool = False
    completion_pending_intake: bool = False
    awaiting_review: bool = False
    review_pass_waiting_integration: bool = False
    capacity_feedback_missing: bool = False
    lane_item_ready: bool = False
    dag_prerequisites_satisfied: bool = False
    exact_authority: bool = False
    authority_compatible: bool = False
    provider_available: bool = True
    capacity_state: CapacityState = "UNKNOWN"
    dispatch_mode: DispatchMode = "MANUAL"
    executor_mode: ExecutorMode = "CODEX"
    promotion_eligible: bool = False
    blocker: str | None = None

@dataclass(frozen=True, slots=True)
class RouteDecision:
    route: str
    execution_allowed: bool
    invocation_allowed: bool
    authority_granted: bool
    proposal_only: bool
    reason: str
    blocker: str | None = None

def _route(route: str, reason: str, *, execution_allowed: bool = False,
           blocker: str | None = None) -> RouteDecision:
    return RouteDecision(route, execution_allowed, False, False, True, reason, blocker)

def resolve_route(snapshot: OrchestrationSnapshot) -> RouteDecision:
    if snapshot.safety_violation or snapshot.authorization_revoked or snapshot.side_effect_violation or snapshot.missing_required_identity:
        return _route("STOP_SAFETY_GOVERNANCE", "safety/governance failure")
    if snapshot.current_contradiction or snapshot.competing_writers or snapshot.executable_identity_count > 1:
        return _route("RECONCILIATION_REQUIRED", "contradictory current state")
    if snapshot.resume_requested or snapshot.paused_execution_exists:
        if not snapshot.paused_execution_exists or not snapshot.paused_executor_invoked or not snapshot.paused_lineage_valid:
            return _route("RECONCILIATION_REQUIRED", "resume cannot fabricate invocation or lineage")
        if snapshot.executor_mode == "CODEX" and not snapshot.provider_available:
            return _route("WAIT_PROVIDER_AVAILABLE", "provider unavailable for existing execution")
        return _route("RESUME_EXISTING_EXECUTION", "valid invoked lineage is resume-first", execution_allowed=True)
    if snapshot.completion_pending_intake:
        return _route("WORK_RESULT_INTAKE", "completion needs intake")
    if snapshot.awaiting_review:
        return _route("WAIT_REVIEW", "review pending")
    if snapshot.review_pass_waiting_integration:
        return _route("WAIT_INTEGRATION", "integration pending")
    if snapshot.executor_mode == "CODEX" and snapshot.capacity_feedback_missing:
        return _route("WORK_CAPACITY_REVIEW", "capacity feedback missing")
    if not snapshot.lane_item_ready:
        return _route("NO_LEGAL_READY_WORK", "lane head not ready", blocker=snapshot.blocker)
    if not snapshot.dag_prerequisites_satisfied:
        return _route("NO_LEGAL_READY_WORK", "DAG prerequisites unsatisfied")
    if not snapshot.exact_authority:
        return _route("WORK_AUTHORIZATION_REQUIRED", "exact authority missing")
    if not snapshot.authority_compatible:
        return _route("STOP_SAFETY_GOVERNANCE", "authority drift")
    if snapshot.executor_mode == "CODEX":
        if not snapshot.provider_available:
            return _route("WAIT_PROVIDER_AVAILABLE", "provider denied")
        if snapshot.capacity_state == "INSUFFICIENT":
            return _route("WORK_CAPACITY_REVIEW", "PRIMARY_5H insufficient")
    if snapshot.dispatch_mode == "CONTROLLED_AUTO":
        if not snapshot.promotion_eligible:
            return _route("NO_LEGAL_READY_WORK", "CONTROLLED_AUTO not promoted")
        return _route("CONTROLLED_AUTO_DISPATCH_ELIGIBLE", "promotion evidence passed", execution_allowed=True)
    return _route("READY_FOR_MANUAL_DISPATCH", "manual authority eligible", execution_allowed=True)

@dataclass(frozen=True, slots=True)
class PromotionEvidence:
    controller_commit: str
    policy_hash: str
    architecture_bundle: str
    capacity_method_identity: str
    provider_pool_identity: str
    exact_pre_existing_authorization: bool
    exact_scope_binding: bool
    valid_single_use_lifecycle: bool
    no_higher_priority_unfinished_item: bool
    single_writer: bool
    provider_available: bool
    no_provisional_unattended_execution: bool
    exact_architecture_policy_compatibility: bool
    stable_dedupe_idempotency: bool
    independent_controller_review_pass: bool
    accepted_manual_executions: int
    zero_duplicate_dispatch: bool
    zero_fabricated_resume_recovery: bool
    exact_local_token_attribution: bool
    no_unresolved_high_critical_governance_anomaly: bool
    owner_controlled_auto_activation: bool
    primary_5h_safe_tokens: int | None
    p90_tokens: int
    weekly_safe_tokens: int | None = None

@dataclass(frozen=True, slots=True)
class PromotionDecision:
    eligible: bool
    missing: tuple[str, ...]

def evaluate_promotion(evidence: PromotionEvidence) -> PromotionDecision:
    checks = (
        ("exact_pre_existing_authorization", evidence.exact_pre_existing_authorization),
        ("exact_scope_binding", evidence.exact_scope_binding),
        ("valid_single_use_lifecycle", evidence.valid_single_use_lifecycle),
        ("no_higher_priority_unfinished_item", evidence.no_higher_priority_unfinished_item),
        ("single_writer", evidence.single_writer),
        ("provider_available", evidence.provider_available),
        ("no_provisional_unattended_execution", evidence.no_provisional_unattended_execution),
        ("exact_architecture_policy_compatibility", evidence.exact_architecture_policy_compatibility),
        ("stable_dedupe_idempotency", evidence.stable_dedupe_idempotency),
        ("independent_controller_review_PASS", evidence.independent_controller_review_pass),
        ("accepted_manual_executions>=5", evidence.accepted_manual_executions >= 5),
        ("zero_duplicate_dispatch", evidence.zero_duplicate_dispatch),
        ("zero_fabricated_resume_recovery", evidence.zero_fabricated_resume_recovery),
        ("exact_local_token_attribution", evidence.exact_local_token_attribution),
        ("no_unresolved_HIGH_CRITICAL_governance_anomaly", evidence.no_unresolved_high_critical_governance_anomaly),
        ("explicit_owner_controlled_auto_activation", evidence.owner_controlled_auto_activation),
        ("primary_5h_safe_tokens>=p90_tokens", evidence.primary_5h_safe_tokens is not None and evidence.primary_5h_safe_tokens >= evidence.p90_tokens),
    )
    missing = tuple(name for name, passed in checks if not passed)
    return PromotionDecision(not missing, missing)

def bounded_context_profile(primary_paths: Sequence[str], *, history_paths: Sequence[str] = (),
                            ambiguity: bool = False, failure: bool = False) -> Mapping[str, object]:
    def unique(paths: Sequence[str]) -> tuple[str, ...]:
        seen: set[str] = set(); ordered: list[str] = []
        for path in paths:
            if path and path not in seen:
                seen.add(path); ordered.append(path)
        return tuple(ordered)
    primary = unique(primary_paths)
    include_history = ambiguity or failure
    history = unique(history_paths) if include_history else ()
    return MappingProxyType({
        "load_order": unique(primary + history),
        "history_loaded": include_history,
        "history_reason": "AMBIGUITY_OR_FAILURE" if include_history else "NOT_REQUIRED",
        "pointer_first": True,
        "authority_effect": "NONE",
    })
