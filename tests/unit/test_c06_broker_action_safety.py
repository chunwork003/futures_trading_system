from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from persistence.account_authority import (
    AccountAuthorityCommit,
    AccountAuthorityCommitService,
    AccountStateHead,
)
from persistence.broker_action import (
    BrokerActionAttempt,
    BrokerActionConflictError,
    BrokerActionHead,
    BrokerActionKind,
    BrokerActionReinvocationDeniedError,
    BrokerActionResolution,
    BrokerActionResolutionKind,
    BrokerActionSafetyService,
    BrokerDispatchOutcome,
    BrokerInvocationResult,
    UnresolvedBrokerActionError,
)


NOW = datetime(2026, 9, 27, 3, tzinfo=timezone.utc)


class Uow:
    def __init__(self): self.active = False; self.committed = False; self.rolled = False
    def __enter__(self): self.active = True; return self
    def commit(self): self.committed = True
    def rollback(self): self.rolled = True
    def __exit__(self, typ, exc, tb):
        self.active = False
        if not self.committed: self.rolled = True
        return False


class AuthorityRepo:
    def __init__(self):
        self.head = AccountStateHead(broker="SINOPAC", account_ref="A", current_revision=1, initialized=True)
        self.receipts = {}; self.checkpoints = {}
    def get_receipt(self, value): return self.receipts.get(value)
    def lock_head(self, broker, account_ref): return self.head
    def lock_or_create_reserved_head(self, broker, account_ref): return self.head
    def get_head(self, broker, account_ref): return self.head
    def get_checkpoint(self, broker, account_ref, revision): return self.checkpoints.get(revision)
    def append_checkpoint(self, value): self.checkpoints[value.account_revision] = value
    def advance_head(self, value, *, expected_revision): self.head = value
    def append_receipt(self, value): self.receipts[value.authority_commit_id] = value


class ActionRepo:
    def __init__(self, fail_attempt=False):
        self.attempts = {}; self.resolutions = {}; self.heads = {}; self.fail_attempt = fail_attempt
    @staticmethod
    def key(attempt): return (attempt.broker, attempt.account_ref, attempt.order_id, attempt.action)
    def get_attempt(self, attempt_id): return self.attempts.get(attempt_id)
    def append_attempt(self, attempt):
        if self.fail_attempt: raise RuntimeError("attempt persistence failed")
        if attempt.attempt_id in self.attempts and self.attempts[attempt.attempt_id] != attempt:
            raise BrokerActionConflictError("attempt conflict")
        self.attempts[attempt.attempt_id] = attempt
    def get_head(self, broker, account_ref, order_id, action):
        return self.heads.get((broker, account_ref, order_id, action))
    def reserve_head(self, attempt, *, expected_version):
        key = self.key(attempt); current = self.heads.get(key)
        if current is None:
            if expected_version != -1: raise BrokerActionConflictError("head version conflict")
            version = 1
        else:
            if current.version != expected_version or current.unresolved_attempt_id is not None:
                raise BrokerActionConflictError("unresolved action")
            version = current.version + 1
        self.heads[key] = BrokerActionHead(
            broker=attempt.broker, account_ref=attempt.account_ref,
            order_id=attempt.order_id, action=attempt.action, version=version,
            unresolved_attempt_id=attempt.attempt_id,
            automatic_invocation_eligible=False,
        )
    def append_resolution(self, resolution): self.resolutions[resolution.resolution_id] = resolution
    def resolve_head(self, attempt, *, resolution_kind, expected_version):
        key = self.key(attempt); current = self.heads[key]
        if current.version != expected_version or current.unresolved_attempt_id != attempt.attempt_id:
            raise BrokerActionConflictError("release conflict")
        self.heads[key] = current.model_copy(
            update={
                "version": current.version + 1,
                "unresolved_attempt_id": None,
                "automatic_invocation_eligible": (
                    resolution_kind is BrokerActionResolutionKind.NOT_DISPATCHED
                ),
            }
        )


def attempt(action=BrokerActionKind.SUBMIT, **updates):
    values = dict(
        attempt_id=f"ATTEMPT-{action.value}-1", broker="SINOPAC", account_ref="A",
        order_id="ORDER-1", action=action, broker_client_order_ref="CLIENT-ORDER-1",
        command_id=f"COMMAND-{action.value}-1", correlation_id="CORR-1",
        authorization_id="AUTHORIZATION-1", created_at=NOW,
    )
    values.update(updates); return BrokerActionAttempt(**values)


def mutation(revision, suffix):
    return AccountAuthorityCommit(
        authority_commit_id=f"AUTH-COMMIT-{suffix}", mutation_fingerprint=f"FP-{suffix}",
        broker="SINOPAC", account_ref="A", expected_head_revision=revision,
        expected_snapshot_id="EXPECTED-SNAPSHOT-1", recorded_at=NOW,
    )


def resolution(item, kind=BrokerActionResolutionKind.NOT_DISPATCHED, **updates):
    values = dict(
        resolution_id=f"RESOLUTION-{item.attempt_id}", attempt_id=item.attempt_id,
        kind=kind, evidence=("transport socket was never opened",), resolved_at=NOW,
        pre_transport_proof="TRANSPORT-GATE-1" if kind is BrokerActionResolutionKind.NOT_DISPATCHED else None,
    )
    values.update(updates); return BrokerActionResolution(**values)


def build(*, fail_attempt=False):
    uows = []; authority = AuthorityRepo(); actions = ActionRepo(fail_attempt)
    def uow_factory():
        item = Uow(); uows.append(item); return item
    service = BrokerActionSafetyService(
        authority_service=AccountAuthorityCommitService(
            uow_factory=uow_factory, repository=lambda _: authority,
        ),
        repository=lambda _: actions,
    )
    return service, uows, authority, actions


@pytest.mark.parametrize("action", list(BrokerActionKind))
def test_attempt_commits_before_submit_or_cancel_invocation(action) -> None:
    service, uows, _, actions = build(); item = attempt(action)
    observed = []
    def invoke(value):
        assert not uows[-1].active
        assert actions.get_attempt(value.attempt_id) == value
        observed.append(value.action)
        return BrokerInvocationResult(outcome=BrokerDispatchOutcome.DISPATCHED, evidence="accepted")
    receipt, result = service.commit_attempt_then_invoke(
        mutation=mutation(1, action.value), attempt=item, invoke=invoke,
    )
    assert receipt.committed_revision == 2
    assert result.outcome is BrokerDispatchOutcome.DISPATCHED
    assert observed == [action]


def test_attempt_commit_failure_means_zero_broker_invocation() -> None:
    service, uows, _, _ = build(fail_attempt=True); calls = []
    with pytest.raises(RuntimeError, match="attempt persistence failed"):
        service.commit_attempt_then_invoke(
            mutation=mutation(1, "FAIL"), attempt=attempt(),
            invoke=lambda value: calls.append(value),
        )
    assert calls == [] and uows[-1].rolled


@pytest.mark.parametrize("action", list(BrokerActionKind))
def test_unresolved_attempt_blocks_automatic_second_invocation_and_duplicate_retry(action) -> None:
    service, _, _, _ = build(); calls = []
    first = attempt(action)
    service.commit_attempt_then_invoke(
        mutation=mutation(1, f"{action.value}-FIRST"), attempt=first,
        invoke=lambda value: calls.append(value.attempt_id),
    )
    with pytest.raises(UnresolvedBrokerActionError):
        service.commit_attempt_then_invoke(
            mutation=mutation(2, f"{action.value}-SECOND"),
            attempt=attempt(
                action, attempt_id=f"ATTEMPT-{action.value}-2",
                command_id=f"COMMAND-{action.value}-2",
            ),
            invoke=lambda value: calls.append(value.attempt_id),
        )
    with pytest.raises(UnresolvedBrokerActionError):
        service.commit_attempt_then_invoke(
            mutation=mutation(1, f"{action.value}-FIRST"), attempt=first,
            invoke=lambda value: calls.append(value.attempt_id),
        )
    assert calls == [f"ATTEMPT-{action.value}-1"]


@pytest.mark.parametrize("evidence", ["zero exact broker matches", "timeout", "connection lost", "response lost"])
def test_unknown_or_zero_match_never_becomes_retry_authority(evidence: str) -> None:
    service, _, _, _ = build(); calls = []
    service.commit_attempt_then_invoke(
        mutation=mutation(1, "UNKNOWN"), attempt=attempt(),
        invoke=lambda value: BrokerInvocationResult(
            outcome=BrokerDispatchOutcome.OUTCOME_UNKNOWN, evidence=evidence
        ),
    )
    with pytest.raises(UnresolvedBrokerActionError):
        service.commit_attempt_then_invoke(
            mutation=mutation(2, "RETRY"),
            attempt=attempt(attempt_id="ATTEMPT-RETRY", command_id="COMMAND-RETRY"),
            invoke=lambda value: calls.append(value),
        )
    assert calls == []


def test_generic_timeout_propagates_and_remains_unresolved() -> None:
    service, _, _, actions = build(); item = attempt()
    with pytest.raises(TimeoutError):
        service.commit_attempt_then_invoke(
            mutation=mutation(1, "TIMEOUT"), attempt=item,
            invoke=lambda _: (_ for _ in ()).throw(TimeoutError("lost response")),
        )
    assert actions.heads[actions.key(item)].unresolved_attempt_id == item.attempt_id


def test_only_durable_proven_not_dispatched_resolution_releases_head() -> None:
    service, _, authority, actions = build(); item = attempt()
    _, observation = service.commit_attempt_then_invoke(
        mutation=mutation(1, "ATTEMPT"), attempt=item,
        invoke=lambda _: BrokerInvocationResult(
            outcome=BrokerDispatchOutcome.NOT_DISPATCHED,
            evidence="transport gate rejected before dispatch",
            pre_transport_proof="TRANSPORT-GATE-1",
        ),
    )
    assert actions.heads[actions.key(item)].unresolved_attempt_id == item.attempt_id
    service.commit_resolution(
        mutation=mutation(2, "RESOLVE"), attempt=item,
        resolution=resolution(item, pre_transport_proof=observation.pre_transport_proof),
    )
    assert actions.heads[actions.key(item)].unresolved_attempt_id is None
    next_item = attempt(attempt_id="ATTEMPT-SUBMIT-2", command_id="COMMAND-SUBMIT-2")
    service.commit_attempt_then_invoke(
        mutation=mutation(3, "NEXT"), attempt=next_item,
        invoke=lambda _: "invoked",
    )
    assert authority.head.current_revision == 4


@pytest.mark.parametrize("action", list(BrokerActionKind))
@pytest.mark.parametrize(
    "resolved_kind",
    [BrokerActionResolutionKind.SUCCEEDED, BrokerActionResolutionKind.FAILED],
)
def test_material_resolution_clears_unresolved_but_denies_same_action_reinvocation(
    action, resolved_kind
) -> None:
    service, _, _, actions = build(); item = attempt(action)
    service.commit_attempt_then_invoke(
        mutation=mutation(1, f"{action.value}-ATTEMPT"),
        attempt=item,
        invoke=lambda _: "dispatched",
    )
    service.commit_resolution(
        mutation=mutation(2, f"{action.value}-{resolved_kind.value}"),
        attempt=item,
        resolution=resolution(item, kind=resolved_kind),
    )
    head = actions.heads[actions.key(item)]
    assert head.unresolved_attempt_id is None
    assert head.automatic_invocation_eligible is False
    calls = []
    with pytest.raises(BrokerActionReinvocationDeniedError):
        service.commit_attempt_then_invoke(
            mutation=mutation(3, f"{action.value}-SECOND"),
            attempt=attempt(
                action,
                attempt_id=f"ATTEMPT-{action.value}-2",
                command_id=f"COMMAND-{action.value}-2",
            ),
            invoke=lambda value: calls.append(value),
        )
    assert calls == []


def test_not_dispatched_cannot_be_claimed_without_positive_proof() -> None:
    with pytest.raises(ValidationError, match="positive pre-transport proof"):
        BrokerInvocationResult(
            outcome=BrokerDispatchOutcome.NOT_DISPATCHED, evidence="generic exception"
        )
    with pytest.raises(ValidationError, match="verified pre-transport proof"):
        resolution(attempt(), pre_transport_proof=None)


def test_client_ref_is_correlation_only_and_no_manual_override_exists() -> None:
    service, _, _, actions = build(); item = attempt()
    service.commit_attempt_then_invoke(
        mutation=mutation(1, "ONE"), attempt=item, invoke=lambda _: "sent"
    )
    different_attempt = attempt(
        attempt_id="ATTEMPT-SUBMIT-2", command_id="COMMAND-SUBMIT-2"
    )
    assert different_attempt.broker_client_order_ref == item.broker_client_order_ref
    with pytest.raises(UnresolvedBrokerActionError):
        service.commit_attempt_then_invoke(
            mutation=mutation(2, "TWO"), attempt=different_attempt,
            invoke=lambda _: "must not run",
        )
    assert actions.heads[actions.key(item)].unresolved_attempt_id == item.attempt_id
    assert not hasattr(service, "manual_release") and not hasattr(service, "force_retry")


def test_durable_head_rejects_concurrent_unresolved_reservation() -> None:
    repo = ActionRepo(); first = attempt(); second = attempt(
        attempt_id="ATTEMPT-SUBMIT-2", command_id="COMMAND-SUBMIT-2"
    )
    repo.reserve_head(first, expected_version=-1)
    with pytest.raises(BrokerActionConflictError):
        repo.reserve_head(second, expected_version=1)
