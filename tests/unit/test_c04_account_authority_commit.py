from datetime import datetime, timezone

import pytest

from persistence.account_authority import (
    AccountAuthorityCommit,
    AccountAuthorityCommitReceipt,
    AccountAuthorityCommitService,
    AccountAuthorityConflictError,
    AccountAuthorityIntegrityError,
    AccountRecoveryCheckpoint,
    AccountStateHead,
)
from persistence.readiness_fence import RecoveryReadinessFenceToken
from trading.account import BrokerAccount


NOW = datetime(2026, 9, 26, 2, tzinfo=timezone.utc)


class Uow:
    def __init__(self): self.committed=False; self.rolled=False
    def __enter__(self): return self
    def commit(self): self.committed=True
    def rollback(self): self.rolled=True
    def __exit__(self, typ, exc, tb):
        if not self.committed: self.rolled=True
        return False


class Repository:
    def __init__(self, fail=None, receipt=None, checkpoint=True):
        self.fail=fail; self.receipt=receipt; self.calls=[]
        revision = 1 if receipt is None else receipt.committed_revision
        self.head=AccountStateHead(
            broker="SINOPAC", account_ref="A",
            current_revision=revision, initialized=True,
        )
        self.checkpoint = (
            AccountRecoveryCheckpoint(
                broker=receipt.broker,
                account_ref=receipt.account_ref,
                account_revision=receipt.committed_revision,
                expected_snapshot_id=receipt.expected_snapshot_id,
                authority_commit_id=receipt.authority_commit_id,
                recorded_at=receipt.recorded_at,
            )
            if receipt is not None and checkpoint
            else None
        )
    def get_receipt(self, value): self.calls.append("get_receipt"); return self.receipt
    def lock_head(self, broker, account_ref): self.calls.append("lock_head"); return self.head
    def lock_or_create_reserved_head(self, broker, account_ref): self.calls.append("bootstrap_head"); return self.head
    def get_head(self, broker, account_ref): self.calls.append("get_head"); return self.head
    def get_checkpoint(self, broker, account_ref, revision): self.calls.append("get_checkpoint"); return self.checkpoint
    def append_checkpoint(self, value): self._call("checkpoint")
    def advance_head(self, value, *, expected_revision): self._call("head"); self.head=value
    def append_receipt(self, value): self._call("receipt"); self.receipt=value
    def _call(self, name):
        self.calls.append(name)
        if self.fail == name: raise RuntimeError(name)
    def lock_active_readiness_fence(self, account):
        return None
    def advance_locked_readiness_fence(self, token):
        raise AssertionError("inactive fence must not advance")


class Participant:
    def __init__(self, name, calls, fail=False): self.name=name; self.calls=calls; self.fail=fail
    def apply(self):
        self.calls.append(self.name)
        if self.fail: raise RuntimeError(self.name)


class FenceRepository:
    def __init__(self,calls,token=None,fail_advance=False):
        self.calls=calls; self.token=token; self.fail_advance=fail_advance
    def lock_active(self,account):
        self.calls.append("lock_fence")
        return self.token
    def advance_locked(self,token):
        self.calls.append("advance_fence")
        if self.fail_advance: raise RuntimeError("advance_fence")
        return token.model_copy(update={"captured_readiness_revision":token.captured_readiness_revision+1})


def _fence_token():
    return RecoveryReadinessFenceToken(account=BrokerAccount(broker="SINOPAC",account_ref="A"),recovery_generation=4,recovery_cut_revision=1,captured_readiness_revision=7)


def mutation(**updates):
    values=dict(authority_commit_id="COMMIT-2", mutation_fingerprint="FP-2", broker="SINOPAC",
                account_ref="A", expected_head_revision=1, expected_snapshot_id="SNAP-2", recorded_at=NOW)
    values.update(updates); return AccountAuthorityCommit(**values)


def test_shared_commit_orders_participants_checkpoint_head_receipt_and_commits_once() -> None:
    uow=Uow(); repo=Repository(); calls=[]
    result=AccountAuthorityCommitService(uow_factory=lambda:uow, repository=lambda _:repo).commit(
        mutation(), participants=(Participant("event", calls), Participant("fill", calls),
                                  Participant("order", calls), Participant("snapshot", calls)),
    )
    assert calls == ["event", "fill", "order", "snapshot"]
    assert repo.calls == ["get_receipt", "lock_head", "checkpoint", "head", "receipt"]
    assert result.committed_revision == 2 and result.expected_snapshot_id == "SNAP-2"
    assert uow.committed and not uow.rolled


@pytest.mark.parametrize("failure", ["event", "fill", "order", "snapshot", "checkpoint", "head", "receipt"])
def test_each_material_failure_rolls_back_complete_authority_unit(failure: str) -> None:
    uow=Uow(); repo=Repository(fail=failure); calls=[]
    participants=tuple(Participant(name, calls, fail=name==failure) for name in ("event","fill","order","snapshot"))
    with pytest.raises(RuntimeError, match=failure):
        AccountAuthorityCommitService(uow_factory=lambda:uow, repository=lambda _:repo).commit(
            mutation(), participants=participants,
        )
    assert uow.rolled and not uow.committed


def test_exact_duplicate_returns_stable_receipt_without_material_effect() -> None:
    prior=AccountAuthorityCommitReceipt(
        authority_commit_id="COMMIT-2", mutation_fingerprint="FP-2", broker="SINOPAC", account_ref="A",
        committed_revision=2, expected_snapshot_id="SNAP-2", recorded_at=NOW,
    )
    uow=Uow(); repo=Repository(receipt=prior); calls=[]
    result=AccountAuthorityCommitService(uow_factory=lambda:uow, repository=lambda _:repo).commit(
        mutation(), participants=(Participant("event", calls),),
    )
    assert result is prior and calls == []
    assert repo.calls == ["get_receipt", "get_checkpoint", "get_head"]
    assert uow.rolled and not uow.committed


def test_same_commit_identity_with_different_semantics_is_explicit_conflict() -> None:
    prior=AccountAuthorityCommitReceipt(
        authority_commit_id="COMMIT-2", mutation_fingerprint="OTHER", broker="SINOPAC", account_ref="A",
        committed_revision=2, expected_snapshot_id="SNAP-2", recorded_at=NOW,
    )
    with pytest.raises(AccountAuthorityConflictError, match="conflicting"):
        AccountAuthorityCommitService(uow_factory=Uow, repository=lambda _:Repository(receipt=prior)).commit(mutation())


def test_generic_commit_cannot_silently_initialize_revision_zero() -> None:
    repo=Repository()
    repo.head=AccountStateHead(
        broker="SINOPAC", account_ref="A", current_revision=0, initialized=False
    )
    with pytest.raises(RuntimeError, match="explicit initialization"):
        AccountAuthorityCommitService(
            uow_factory=Uow, repository=lambda _:repo
        ).commit(mutation(expected_head_revision=0))


def test_duplicate_receipt_missing_or_mismatched_checkpoint_fails_closed() -> None:
    prior=AccountAuthorityCommitReceipt(
        authority_commit_id="COMMIT-2", mutation_fingerprint="FP-2", broker="SINOPAC", account_ref="A",
        committed_revision=2, expected_snapshot_id="SNAP-2", recorded_at=NOW,
    )
    with pytest.raises(AccountAuthorityIntegrityError, match="incomplete durable closure"):
        AccountAuthorityCommitService(
            uow_factory=Uow, repository=lambda _:Repository(receipt=prior, checkpoint=False)
        ).commit(mutation())

    repo=Repository(receipt=prior)
    repo.checkpoint=repo.checkpoint.model_copy(update={"expected_snapshot_id":"OTHER"})
    with pytest.raises(AccountAuthorityIntegrityError, match="exact expected snapshot"):
        AccountAuthorityCommitService(
            uow_factory=Uow, repository=lambda _:repo
        ).commit(mutation())


def test_historical_duplicate_receipt_allows_current_head_to_be_ahead() -> None:
    prior=AccountAuthorityCommitReceipt(
        authority_commit_id="COMMIT-2", mutation_fingerprint="FP-2", broker="SINOPAC", account_ref="A",
        committed_revision=2, expected_snapshot_id="SNAP-2", recorded_at=NOW,
    )
    repo=Repository(receipt=prior)
    repo.head=AccountStateHead(
        broker="SINOPAC", account_ref="A", current_revision=5, initialized=True
    )
    calls=[]
    result=AccountAuthorityCommitService(
        uow_factory=Uow, repository=lambda _:repo
    ).commit(mutation(), participants=(Participant("economic", calls),))
    assert result == prior
    assert calls == []


def test_duplicate_receipt_rejects_head_behind_historical_revision() -> None:
    prior=AccountAuthorityCommitReceipt(
        authority_commit_id="COMMIT-2", mutation_fingerprint="FP-2", broker="SINOPAC", account_ref="A",
        committed_revision=2, expected_snapshot_id="SNAP-2", recorded_at=NOW,
    )
    repo=Repository(receipt=prior)
    repo.head=AccountStateHead(
        broker="SINOPAC", account_ref="A", current_revision=1, initialized=True
    )
    with pytest.raises(AccountAuthorityIntegrityError, match="behind checkpoint"):
        AccountAuthorityCommitService(
            uow_factory=Uow, repository=lambda _:repo
        ).commit(mutation())


def test_d1a_new_material_commit_locks_before_head_and_advances_once() -> None:
    uow=Uow(); repo=Repository(); fence=FenceRepository(repo.calls,_fence_token())
    repo.lock_active_readiness_fence=fence.lock_active
    repo.advance_locked_readiness_fence=fence.advance_locked
    result=AccountAuthorityCommitService(uow_factory=lambda:uow,repository=lambda _:repo).commit(mutation())
    assert result.committed_revision == 2
    assert repo.calls == ["get_receipt","lock_fence","lock_head","checkpoint","head","receipt","advance_fence"]
    assert uow.committed and not uow.rolled


def test_d1a_duplicate_and_conflicting_receipts_never_lock_or_advance_fence() -> None:
    prior=AccountAuthorityCommitReceipt(authority_commit_id="COMMIT-2",mutation_fingerprint="FP-2",broker="SINOPAC",account_ref="A",committed_revision=2,expected_snapshot_id="SNAP-2",recorded_at=NOW)
    for fingerprint,raises in (("FP-2",False),("OTHER",True)):
        repo=Repository(receipt=prior.model_copy(update={"mutation_fingerprint":fingerprint})); calls=[]
        fence=FenceRepository(calls,_fence_token()); repo.lock_active_readiness_fence=fence.lock_active; repo.advance_locked_readiness_fence=fence.advance_locked
        service=AccountAuthorityCommitService(uow_factory=Uow,repository=lambda _:repo)
        if raises:
            with pytest.raises(AccountAuthorityConflictError): service.commit(mutation())
        else: service.commit(mutation())
        assert calls == []


def test_d1a_participant_failure_never_advances_fence_or_commits() -> None:
    uow=Uow(); repo=Repository(); calls=[]; fence=FenceRepository(calls,_fence_token())
    repo.lock_active_readiness_fence=fence.lock_active; repo.advance_locked_readiness_fence=fence.advance_locked
    with pytest.raises(RuntimeError,match="material"):
        AccountAuthorityCommitService(uow_factory=lambda:uow,repository=lambda _:repo).commit(mutation(),participants=(Participant("material",calls,fail=True),))
    assert calls == ["lock_fence","material"]
    assert uow.rolled and not uow.committed


def test_d1a_rf01_missing_fence_contract_fails_before_head_or_material() -> None:
    inner=Repository(); calls=[]
    class LegacyRepository:
        def get_receipt(self,value): return inner.get_receipt(value)
        def lock_head(self,*args): calls.append("lock_head"); return inner.lock_head(*args)
        def append_checkpoint(self,value): inner.append_checkpoint(value)
        def advance_head(self,value,*,expected_revision): inner.advance_head(value,expected_revision=expected_revision)
        def append_receipt(self,value): inner.append_receipt(value)
    uow=Uow()
    with pytest.raises(AttributeError,match="lock_active_readiness_fence"):
        AccountAuthorityCommitService(uow_factory=lambda:uow,repository=lambda _:LegacyRepository()).commit(
            mutation(),participants=(Participant("material",calls),)
        )
    assert calls == []
    assert uow.rolled and not uow.committed


def test_d1a_rf01_explicit_no_active_fence_allows_ordinary_commit() -> None:
    uow=Uow(); repo=Repository()
    result=AccountAuthorityCommitService(uow_factory=lambda:uow,repository=lambda _:repo).commit(mutation())
    assert result.committed_revision == 2 and uow.committed


def test_d1a_rf01_fence_advance_failure_rolls_back_complete_unit() -> None:
    uow=Uow(); repo=Repository(); calls=[]; fence=FenceRepository(calls,_fence_token(),fail_advance=True)
    repo.lock_active_readiness_fence=fence.lock_active
    repo.advance_locked_readiness_fence=fence.advance_locked
    with pytest.raises(RuntimeError,match="advance_fence"):
        AccountAuthorityCommitService(uow_factory=lambda:uow,repository=lambda _:repo).commit(
            mutation(),participants=(Participant("material",calls),)
        )
    assert calls == ["lock_fence","material","advance_fence"]
    assert repo.calls == ["get_receipt","lock_head","checkpoint","head","receipt"]
    assert uow.rolled and not uow.committed
