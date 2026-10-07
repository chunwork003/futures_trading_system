from __future__ import annotations

import pytest

from automation.engine.orchestration import (
    OrchestrationSnapshot, PromotionEvidence, QueueItem,
    QueueReconciliationRequired, StaleProjectionError, WakeEvent,
    bounded_context_profile, dedupe_key, evaluate_promotion, project_queue,
    resolve_route,
)

def _event(event_class: str = "MANUAL_CONTINUE") -> WakeEvent:
    return WakeEvent(event_class, "AUTO-IMP-002", "a" * 40, 3, "CURRENT")

def _item(*, event_class="MANUAL_CONTINUE", priority_class="AUTHORIZED_NEW_WORK",
          state="WAITING", subject="AUTO-IMP-002", lane_position=0) -> QueueItem:
    event = _event(event_class)
    return QueueItem.build(
        queue_item_id=f"Q-{subject}-{event_class}", subject_id=subject,
        package_id=subject, work_order_id=f"WO-{subject}", execution_id=None,
        item_kind="PACKAGE", architecture_policy_identity="ARCH-1.2.2",
        source_revision="b" * 40, current_relevant_revision=event.relevant_revision,
        lifecycle_generation=event.lifecycle_generation, priority_class=priority_class,
        originating_event=event.event_class, queue_state=state, blocking_reason=None,
        authority_ref=None, lifecycle_ref=None, writer_lease_ref=None,
        created_evidence="created", updated_evidence="updated",
        lane_position=lane_position, dag_ready=True,
    )

def _snapshot(**overrides: object) -> OrchestrationSnapshot:
    values: dict[str, object] = {
        "fresh_master_sha": "a" * 40,
        "active_architecture_policy_hashes": ("ARCH-1.2.2",),
        "current_relevant_revision": "b" * 40,
        "lifecycle_generation": 1,
        "lane_item_ready": True,
        "dag_prerequisites_satisfied": True,
        "exact_authority": True,
        "authority_compatible": True,
        "provider_available": True,
        "capacity_state": "FIT",
        "dispatch_mode": "MANUAL",
        "executor_mode": "CODEX",
    }
    values.update(overrides)
    return OrchestrationSnapshot(**values)

def _promotion(**overrides: object) -> PromotionEvidence:
    values: dict[str, object] = {
        "controller_commit": "a" * 40, "policy_hash": "b" * 64,
        "architecture_bundle": "c" * 64, "capacity_method_identity": "CAPACITY-2.2",
        "provider_pool_identity": "provider/account/PRIMARY_5H",
        "exact_pre_existing_authorization": True, "exact_scope_binding": True,
        "valid_single_use_lifecycle": True, "no_higher_priority_unfinished_item": True,
        "single_writer": True, "provider_available": True,
        "no_provisional_unattended_execution": True,
        "exact_architecture_policy_compatibility": True,
        "stable_dedupe_idempotency": True, "independent_controller_review_pass": True,
        "accepted_manual_executions": 5, "zero_duplicate_dispatch": True,
        "zero_fabricated_resume_recovery": True, "exact_local_token_attribution": True,
        "no_unresolved_high_critical_governance_anomaly": True,
        "owner_controlled_auto_activation": True,
        "primary_5h_safe_tokens": 12_000_000, "p90_tokens": 12_000_000,
        "weekly_safe_tokens": 0,
    }
    values.update(overrides)
    return PromotionEvidence(**values)

def test_dedupe_key_ignores_wake_event_class_and_wallclock() -> None:
    first = _event("MANUAL_CONTINUE"); second = _event("SCHEDULED_TIMER_WAKE")
    assert dedupe_key(subject_id=first.subject_id, item_kind="PACKAGE", relevant_revision=first.relevant_revision,
                      lifecycle_generation=first.lifecycle_generation) == dedupe_key(
                      subject_id=second.subject_id, item_kind="PACKAGE", relevant_revision=second.relevant_revision,
                      lifecycle_generation=second.lifecycle_generation)

def test_project_queue_collapses_same_state_across_wake_classes() -> None:
    projected = project_queue((_item(event_class="MANUAL_CONTINUE"), _item(event_class="SCHEDULED_TIMER_WAKE")))
    assert len(projected) == 1

def test_project_queue_rejects_multiple_executable_or_in_progress_items() -> None:
    with pytest.raises(QueueReconciliationRequired):
        project_queue((_item(subject="AUTO-IMP-002", state="ELIGIBLE_MANUAL", lane_position=0),
                       _item(subject="AUTO-IMP-003", state="IN_PROGRESS", lane_position=1)))

def test_project_queue_rejects_stale_compare_and_swap() -> None:
    with pytest.raises(StaleProjectionError):
        project_queue((_item(),), expected_master="a"*40, actual_master="b"*40,
                      expected_generation=2, actual_generation=2)

def test_queue_priority_places_unfinished_before_new_work() -> None:
    projected = project_queue((_item(subject="AUTO-IMP-003", priority_class="AUTHORIZED_NEW_WORK", lane_position=1),
                               _item(subject="EXEC-OLD", priority_class="RESUMABLE_UNFINISHED_EXECUTION", lane_position=99)))
    assert projected[0].subject_id == "EXEC-OLD"

@pytest.mark.parametrize(("snapshot", "expected"), [
    (_snapshot(safety_violation=True), "STOP_SAFETY_GOVERNANCE"),
    (_snapshot(current_contradiction=True), "RECONCILIATION_REQUIRED"),
    (_snapshot(competing_writers=True), "RECONCILIATION_REQUIRED"),
    (_snapshot(executable_identity_count=2), "RECONCILIATION_REQUIRED"),
    (_snapshot(completion_pending_intake=True), "WORK_RESULT_INTAKE"),
    (_snapshot(awaiting_review=True), "WAIT_REVIEW"),
    (_snapshot(review_pass_waiting_integration=True), "WAIT_INTEGRATION"),
    (_snapshot(lane_item_ready=False), "NO_LEGAL_READY_WORK"),
    (_snapshot(dag_prerequisites_satisfied=False), "NO_LEGAL_READY_WORK"),
    (_snapshot(exact_authority=False), "WORK_AUTHORIZATION_REQUIRED"),
    (_snapshot(provider_available=False), "WAIT_PROVIDER_AVAILABLE"),
    (_snapshot(capacity_state="INSUFFICIENT"), "WORK_CAPACITY_REVIEW"),
    (_snapshot(), "READY_FOR_MANUAL_DISPATCH"),
])
def test_route_decision_table(snapshot: OrchestrationSnapshot, expected: str) -> None:
    decision = resolve_route(snapshot)
    assert decision.route == expected
    assert decision.invocation_allowed is False
    assert decision.authority_granted is False

def test_paused_invoked_execution_is_resume_first() -> None:
    assert resolve_route(_snapshot(resume_requested=True, paused_execution_exists=True,
        paused_executor_invoked=True, paused_lineage_valid=True)).route == "RESUME_EXISTING_EXECUTION"

def test_paused_invoked_execution_waits_for_provider_when_codex_denied() -> None:
    assert resolve_route(_snapshot(resume_requested=True, paused_execution_exists=True,
        paused_executor_invoked=True, paused_lineage_valid=True,
        provider_available=False)).route == "WAIT_PROVIDER_AVAILABLE"

def test_consumed_never_invoked_is_not_fabricated_resume() -> None:
    assert resolve_route(_snapshot(resume_requested=True, paused_execution_exists=True,
        paused_executor_invoked=False, paused_lineage_valid=True)).route == "RECONCILIATION_REQUIRED"

def test_manual_unknown_capacity_is_allow_with_watch() -> None:
    assert resolve_route(_snapshot(capacity_state="UNKNOWN")).route == "READY_FOR_MANUAL_DISPATCH"

def test_human_dialogue_does_not_use_codex_provider_or_capacity_gate() -> None:
    assert resolve_route(_snapshot(executor_mode="HUMAN_DIALOGUE", provider_available=False,
        capacity_state="INSUFFICIENT")).route == "READY_FOR_MANUAL_DISPATCH"

def test_controlled_auto_requires_promotion() -> None:
    assert resolve_route(_snapshot(dispatch_mode="CONTROLLED_AUTO", promotion_eligible=False)).route == "NO_LEGAL_READY_WORK"
    assert resolve_route(_snapshot(dispatch_mode="CONTROLLED_AUTO", promotion_eligible=True)).route == "CONTROLLED_AUTO_DISPATCH_ELIGIBLE"

def test_controlled_auto_requires_five_manual_executions() -> None:
    result = evaluate_promotion(_promotion(accepted_manual_executions=4))
    assert not result.eligible and "accepted_manual_executions>=5" in result.missing

def test_controlled_auto_uses_primary_5h_p90_not_weekly() -> None:
    result = evaluate_promotion(_promotion(primary_5h_safe_tokens=12_000_000, p90_tokens=12_000_000, weekly_safe_tokens=0))
    assert result.eligible and result.missing == ()

def test_controlled_auto_rejects_primary_5h_below_p90() -> None:
    result = evaluate_promotion(_promotion(primary_5h_safe_tokens=11_999_999, p90_tokens=12_000_000))
    assert not result.eligible and "primary_5h_safe_tokens>=p90_tokens" in result.missing

def test_bounded_context_profile_is_pointer_first_and_history_on_demand() -> None:
    normal = bounded_context_profile(("CURRENT", "WO", "SOURCE", "SOURCE"), history_paths=("OLD-1", "OLD-2"))
    failure = bounded_context_profile(("CURRENT", "WO", "SOURCE"), history_paths=("OLD-1",), failure=True)
    assert normal["load_order"] == ("CURRENT", "WO", "SOURCE") and normal["history_loaded"] is False
    assert failure["load_order"] == ("CURRENT", "WO", "SOURCE", "OLD-1") and failure["history_loaded"] is True

def test_wake_event_is_non_authority_value_object() -> None:
    event = _event("PROVIDER_AVAILABILITY_RECOVERY")
    assert event.effect == "WAKE_ONLY" and event.grants_authority is False and event.dispatches is False


def test_program_v2_declares_permanent_manual_executor_fallback() -> None:
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    program = json.loads(
        (
            root
            / "automation/programs/AUTO-IMP-PROGRAM-V2/program.yaml"
        ).read_text(encoding="utf-8")
    )

    strategy = program["implementation_strategy"]

    assert strategy["supported_dispatch_modes"] == ["MANUAL", "CONTROLLED_AUTO"]
    assert strategy["supported_executor_modes"] == ["HUMAN_DIALOGUE", "CODEX"]
    assert strategy["permanent_manual_fallback"]["supported"] is True
    assert (
        strategy["permanent_manual_fallback"]["human_dialogue_codex_capacity_gate"]
        == "NOT_APPLICABLE"
    )
    assert (
        strategy["permanent_manual_fallback"]["same_execution_multi_executor"]
        == "DENIED"
    )
    assert strategy["controlled_auto"] == "DISABLED"
