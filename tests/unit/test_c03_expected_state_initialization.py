from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from persistence.account import (
    BrokerPositionObservation,
    ExpectedSnapshotIntegrityError,
    ExpectedStateReadError,
)
from persistence.account_authority import (
    AccountAuthorityCommitService,
    AccountAuthorityConflictError,
    AccountAuthorityIntegrityError,
    AccountStateHead,
    ExpectedStateInitializationError,
    ExpectedStateInitializationMode,
    ExpectedStateInitializationRequest,
    ExpectedStateInitializationService,
    InitializationCurrentnessEvidence,
)
from persistence.events import EventAppendResult, EventAppendStatus
from trading.account import AccountPosition, BrokerPositionSnapshot, PositionDirection
from trading.authorization import (
    AuthorizationDecision,
    AuthorizationEnvironment,
    ProtectedActionAuthorization,
    ProtectedActionAuthorizationError,
)


NOW = datetime(2026, 9, 26, 4, tzinfo=timezone.utc)


class Uow:
    def __init__(self): self.committed=False; self.rolled=False
    def __enter__(self): return self
    def commit(self): self.committed=True
    def rollback(self): self.rolled=True
    def __exit__(self, typ, exc, tb):
        if not self.committed: self.rolled=True
        return False


class AuthorityRepo:
    def __init__(self):
        self.head=AccountStateHead(broker="SINOPAC", account_ref="A", current_revision=0, initialized=False)
        self.receipts={}; self.checkpoints=[]
    def get_receipt(self, key): return self.receipts.get(key)
    def lock_head(self, broker, account_ref): return self.head
    def append_checkpoint(self, value): self.checkpoints.append(value)
    def advance_head(self, value, *, expected_revision):
        if self.head.current_revision != expected_revision: raise AccountAuthorityConflictError("head conflict")
        self.head=value
    def append_receipt(self, value): self.receipts[value.authority_commit_id]=value


class AppendRepo:
    def __init__(self, event=False, error=None): self.items=[]; self.event=event; self.error=error
    def append(self, value):
        if self.error: raise self.error
        self.items.append(value)
        if self.event: return EventAppendResult(status=EventAppendStatus.APPENDED, event_id=value.event_id)


class AuthorizationProvider:
    environment=AuthorizationEnvironment.TEST
    def __init__(self, item): self.item=item
    def verify(self, authorization_id): return self.item


class CurrentnessProvider:
    environment=AuthorizationEnvironment.TEST
    def __init__(self, item): self.item=item
    def verify(self, fingerprint): return self.item


def auth():
    return ProtectedActionAuthorization(
        authorization_id="AUTH-INIT", principal_id="USER", policy_id="POLICY", policy_version="V1",
        action="EXPECTED_STATE_INITIALIZE", resource="SINOPAC:A", protected_world_fingerprint="WORLD",
        command_id="CMD", correlation_id="CORR", decision=AuthorizationDecision.APPROVED,
        provenance="TEST", authorized_at=NOW, environment=AuthorizationEnvironment.TEST,
    )


def currentness():
    return InitializationCurrentnessEvidence(
        evidence_id="CURRENT-1", protected_world_fingerprint="WORLD",
        environment=AuthorizationEnvironment.TEST,
    )


def broker_position():
    return BrokerPositionSnapshot(
        broker="SINOPAC", account_ref="A", instrument_id=1, contract_id=101,
        direction=PositionDirection.LONG, quantity=2, observed_at=NOW,
    )


def expected_position():
    return AccountPosition(
        broker="SINOPAC", account_ref="A", instrument_id=1, contract_id=101,
        direction=PositionDirection.LONG, quantity=2,
    )


def request(mode=ExpectedStateInitializationMode.FLAT, **updates):
    positions=() if mode is ExpectedStateInitializationMode.FLAT else (expected_position(),)
    actual=() if mode is ExpectedStateInitializationMode.FLAT else (broker_position(),)
    values=dict(
        event_id="INIT-EVENT", snapshot_id="INIT-SNAPSHOT", authority_commit_id="INIT-COMMIT",
        mutation_fingerprint="INIT-FP", mode=mode,
        observation=BrokerPositionObservation(
            observation_id="OBS-1", broker="SINOPAC", account_ref="A",
            observed_at=NOW, recorded_at=NOW, positions=actual,
        ),
        seeded_positions=positions, confirmed_by="USER", confirmed_at=NOW,
        reason=None if mode is ExpectedStateInitializationMode.FLAT else "approved seed",
        authorization_id="AUTH-INIT", command_id="CMD", correlation_id="CORR",
        protected_world_fingerprint="WORLD", environment=AuthorizationEnvironment.TEST,
    )
    values.update(updates); return ExpectedStateInitializationRequest(**values)


def service(authority_repo=None, event_repo=None, snapshot_repo=None, observation_repo=None):
    uow=Uow(); authority_repo=authority_repo or AuthorityRepo()
    event_repo=event_repo or AppendRepo(event=True); snapshot_repo=snapshot_repo or AppendRepo()
    observation_repo=observation_repo or AppendRepo()
    authority=AccountAuthorityCommitService(uow_factory=lambda:uow, repository=lambda _:authority_repo)
    item=ExpectedStateInitializationService(
        authority_service=authority,
        initialization_repositories=lambda _: (event_repo, snapshot_repo, observation_repo),
    )
    return item,uow,authority_repo,event_repo,snapshot_repo,observation_repo


@pytest.mark.parametrize("mode", [ExpectedStateInitializationMode.FLAT, ExpectedStateInitializationMode.BROKER_SEED])
def test_initialization_builds_atomic_revision_one_exact_closure(mode) -> None:
    item,uow,repo,events,snapshots,observations=service()
    receipt=item.initialize(request(mode), authorization_provider=AuthorizationProvider(auth()),
                            currentness_provider=CurrentnessProvider(currentness()))
    assert receipt.committed_revision == 1 and repo.head.current_revision == 1
    assert repo.checkpoints[0].expected_snapshot_id == "INIT-SNAPSHOT"
    assert events.items[0].event_type == "EXPECTED_STATE_INITIALIZED"
    assert snapshots.items[0].source_event_id == "INIT-EVENT"
    assert snapshots.items[0].positions == request(mode).seeded_positions
    assert observations.items[0].observation_id == "OBS-1"
    assert uow.committed
    assert not hasattr(receipt, "ready")


def test_broker_seed_requires_exact_nonempty_observation_reason_and_positions() -> None:
    with pytest.raises(ValidationError): request(ExpectedStateInitializationMode.BROKER_SEED, reason=" ")
    with pytest.raises(ValidationError, match="derive exactly"):
        request(ExpectedStateInitializationMode.BROKER_SEED, seeded_positions=(expected_position().model_copy(update={"quantity":1}),))


def test_flat_is_explicit_and_never_inferred_from_missing_or_failed_read() -> None:
    item,uow,repo,*_=service(authority_repo=AuthorityRepo())
    repo.head=None
    with pytest.raises(AccountAuthorityIntegrityError, match="head is missing"):
        item.initialize(request(), authorization_provider=AuthorizationProvider(auth()),
                        currentness_provider=CurrentnessProvider(currentness()))
    assert uow.rolled
    for error in (ExpectedStateReadError("read"), ExpectedSnapshotIntegrityError("integrity")):
        failing_service, failing_uow, *_rest = service(
            observation_repo=AppendRepo(error=error)
        )
        with pytest.raises(type(error)):
            failing_service.initialize(
                request(),
                authorization_provider=AuthorizationProvider(auth()),
                currentness_provider=CurrentnessProvider(currentness()),
            )
        assert failing_uow.rolled


def test_initialization_idempotent_replay_and_competing_content_conflict() -> None:
    item,_,repo,events,snapshots,observations=service()
    first=item.initialize(request(), authorization_provider=AuthorizationProvider(auth()),
                          currentness_provider=CurrentnessProvider(currentness()))
    second=item.initialize(request(), authorization_provider=AuthorizationProvider(auth()),
                           currentness_provider=CurrentnessProvider(currentness()))
    assert second == first
    assert len(events.items) == len(snapshots.items) == len(observations.items) == 1
    with pytest.raises(AccountAuthorityConflictError):
        item.initialize(request(mutation_fingerprint="OTHER"), authorization_provider=AuthorizationProvider(auth()),
                        currentness_provider=CurrentnessProvider(currentness()))


def test_production_metadata_or_missing_currentness_cannot_initialize() -> None:
    item,*_=service()
    with pytest.raises(ProtectedActionAuthorizationError):
        item.initialize(request(environment=AuthorizationEnvironment.PRODUCTION),
                        authorization_provider=None, currentness_provider=None)
    with pytest.raises(ExpectedStateInitializationError, match="currentness"):
        item.initialize(request(), authorization_provider=AuthorizationProvider(auth()), currentness_provider=None)


def test_initialization_has_no_order_fill_or_broker_io_capability() -> None:
    item,*_=service()
    assert not hasattr(item, "submit_order")
    assert not hasattr(item, "append_fill")
    assert not hasattr(item, "query_broker")
