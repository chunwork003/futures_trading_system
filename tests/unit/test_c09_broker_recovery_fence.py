from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from persistence.broker_recovery import (
    AccountRecoveryControl, BrokerRecoveryEvidenceService, BrokerReportApplication,
    BrokerReportApplicationStatus, BrokerReportConflictError, BrokerReportInboxEntry,
    BrokerReportIngressStatus, ExecutionContinuityEpoch, RecoveryFenceConflictError,
    ContinuityAuthorityConflictError, ContinuityTransitionReceipt,
    ExecutionContinuityHead, SequenceGap,
)
from trading.account import BrokerAccount

NOW = datetime(2026, 9, 27, 6, tzinfo=timezone.utc)
ACCOUNT = BrokerAccount(broker="SINOPAC", account_ref="A")


class Uow:
    def __init__(self): self.committed=False; self.rolled=False
    def __enter__(self): return self
    def commit(self): self.committed=True
    def rollback(self): self.rolled=True
    def __exit__(self, typ, exc, tb):
        if not self.committed: self.rolled=True
        return False


class Repo:
    def __init__(self): self.inbox={}; self.apps=[]; self.gaps=[]; self.epochs=[]; self.control=None; self.ingress_version=0; self.head=None; self.transitions={}
    def append_inbox(self, item):
        existing=self.inbox.get(item.ingress_id)
        if existing is not None:
            if existing != item: raise BrokerReportConflictError("ingress conflict")
            return BrokerReportIngressStatus.DUPLICATE
        if self.control is None: raise RecoveryFenceConflictError("missing control")
        if self.control.generation != item.generation:
            raise RecoveryFenceConflictError("stale generation")
        self.inbox[item.ingress_id]=item
        if self.control.active:
            self.ingress_version += 1
            self.control=self.control.model_copy(update={"ingress_version":self.ingress_version,"readiness_revision":self.control.readiness_revision+1})
        return BrokerReportIngressStatus.APPENDED
    def append_application(self, item):
        for existing in self.apps:
            if existing.application_id == item.application_id:
                if existing != item: raise BrokerReportConflictError("application conflict")
                return
        if item.ingress_id not in self.inbox or self.inbox[item.ingress_id].generation != item.generation:
            raise BrokerReportConflictError("application ingress generation mismatch")
        prior=max((a.application_sequence for a in self.apps if a.ingress_id == item.ingress_id and a.generation == item.generation),default=0)
        if item.application_sequence != prior + 1:
            raise BrokerReportConflictError("application sequence must be contiguous")
        self.apps.append(item)
        if self.control is not None and self.control.active:
            self.control=self.control.model_copy(update={"readiness_revision":self.control.readiness_revision+1})
    def append_sequence_gap(self, item):
        self.gaps.append(item)
        if self.control is not None and self.control.active:
            self.control=self.control.model_copy(update={"readiness_revision":self.control.readiness_revision+1})
    def append_continuity_epoch(self, item): self.epochs.append(item)
    def transition_continuity_head(self, *, epoch, head, receipt, expected_head_revision, expected_readiness_revision):
        scope=(epoch.broker,epoch.account_ref,epoch.generation)
        if scope != (head.broker,head.account_ref,head.generation) or scope != (receipt.broker,receipt.account_ref,receipt.generation) or epoch.epoch_id != head.current_epoch_id or epoch.epoch_id != receipt.current_epoch_id or head.transition_receipt_id != receipt.transition_id or head.head_revision != receipt.head_revision or head.readiness_revision != receipt.readiness_revision or receipt.previous_head_revision != expected_head_revision or receipt.previous_readiness_revision != expected_readiness_revision:
            raise ContinuityAuthorityConflictError("continuity coherence conflict")
        existing=self.transitions.get(receipt.transition_id)
        if existing is not None:
            if existing != receipt: raise ContinuityAuthorityConflictError("continuity transition identity conflict")
            return
        actual=0 if self.head is None else self.head.head_revision
        if actual != expected_head_revision or self.control is None or not self.control.active or self.control.readiness_revision != expected_readiness_revision:
            raise ContinuityAuthorityConflictError("continuity authority CAS conflict")
        if (epoch.broker,epoch.account_ref,epoch.generation)!=(head.broker,head.account_ref,head.generation):
            raise ContinuityAuthorityConflictError("continuity scope conflict")
        self.epochs.append(epoch); self.head=head; self.transitions[receipt.transition_id]=receipt
        self.control=self.control.model_copy(update={"readiness_revision":self.control.readiness_revision+1})
    def get_control(self, account): return self.control
    def begin_recovery(self, control, *, expected_generation):
        if control.readiness_revision != 0: raise RecoveryFenceConflictError("fresh recovery readiness revision must be zero")
        self.control=control
    def finalize_handoff(self, control, *, expected_generation, expected_ingress_version, expected_readiness_revision):
        if not self.control.active or self.control.generation != expected_generation or self.control.ingress_version != expected_ingress_version or self.control.readiness_revision != expected_readiness_revision:
            raise RecoveryFenceConflictError("stale fence")
        latest={}
        for item in self.apps:
            key=(item.ingress_id,item.generation)
            if key not in latest or item.application_sequence > latest[key].application_sequence:
                latest[key]=item
        resolved=(BrokerReportApplicationStatus.APPLIED,BrokerReportApplicationStatus.DUPLICATE,BrokerReportApplicationStatus.CORROBORATED)
        pending={key for key,item in self.inbox.items() if item.generation == expected_generation and ((key,item.generation) not in latest or latest[(key,item.generation)].status not in resolved)}
        if pending: raise RecoveryFenceConflictError("pending report")
        self.control=control


def entry(**updates):
    values=dict(ingress_id="IN-1", broker="SINOPAC", account_ref="A", generation=1, received_at=NOW, report_type="ORDER", payload_fingerprint="FP-1", payload_json={"status":"Submitted"})
    values.update(updates); return BrokerReportInboxEntry(**values)


def application(status=BrokerReportApplicationStatus.APPLIED, **updates):
    values=dict(application_id=f"APP-{status.value}", ingress_id="IN-1", generation=1, application_sequence=1, status=status, recorded_at=NOW, evidence=("classified exact ingress",))
    values.update(updates); return BrokerReportApplication(**values)


def transition_receipt(**updates):
    values=dict(
        transition_id="TR-1",broker="SINOPAC",account_ref="A",generation=1,
        previous_epoch_id=None,current_epoch_id="EPOCH-2",previous_head_revision=0,
        head_revision=1,previous_readiness_revision=0,readiness_revision=1,
        recovery_cut_fingerprint="CUT-FP",anchor_fingerprint="ANCHOR-FP",
        ingress_version=0,account_revision=7,expected_snapshot_id="SNAP-7",
        authority_commit_id="COMMIT-7",gap_set_fingerprint="GAPS-FP",
        producer_id="RECOVERY",contract_version="W4R-A-V1",evidence_id="EVIDENCE-1",
        recorded_at=NOW,evidence=("re-anchor",),
    )
    values.update(updates)
    return ContinuityTransitionReceipt(**values)


def service(repo):
    uows=[]
    def factory(): item=Uow(); uows.append(item); return item
    return BrokerRecoveryEvidenceService(uow_factory=factory, repository=lambda _:repo), uows


def test_inbox_is_immutable_and_exact_duplicate_is_idempotent() -> None:
    repo=Repo(); repo.control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=1,recovery_cut_revision=7,ingress_version=0,active=True,recorded_at=NOW); svc,uows=service(repo); item=entry()
    assert svc.capture(item) is BrokerReportIngressStatus.APPENDED
    assert svc.capture(item) is BrokerReportIngressStatus.DUPLICATE
    assert len(repo.inbox)==1 and all(u.committed for u in uows)
    assert repo.control.ingress_version == 1
    assert repo.control.readiness_revision == 1
    with pytest.raises(ValidationError): item.payload_fingerprint="OTHER"


def test_same_ingress_identity_with_conflicting_content_fails_closed() -> None:
    repo=Repo(); repo.control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=1,recovery_cut_revision=7,ingress_version=0,active=True,recorded_at=NOW); svc,_=service(repo); svc.capture(entry())
    with pytest.raises(BrokerReportConflictError): svc.capture(entry(payload_fingerprint="OTHER"))


def test_application_statuses_are_exact_and_append_only() -> None:
    assert {item.value for item in BrokerReportApplicationStatus} == {"APPLIED","DUPLICATE","CORROBORATED","DEFERRED","CONFLICT"}
    repo=Repo(); repo.control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=1,recovery_cut_revision=7,ingress_version=0,active=True,recorded_at=NOW); svc,_=service(repo); svc.capture(entry())
    for sequence,status in enumerate(BrokerReportApplicationStatus,1): svc.record_application(application(status, application_id=f"APP-{status.value}",application_sequence=sequence))
    assert [a.status for a in repo.apps] == list(BrokerReportApplicationStatus)


def test_post_cut_report_is_captured_deferred_and_blocks_handoff() -> None:
    repo=Repo(); svc,_=service(repo)
    repo.control=AccountRecoveryControl(broker="SINOPAC", account_ref="A", generation=1, recovery_cut_revision=7, ingress_version=0, active=True, recorded_at=NOW)
    svc.capture(entry())
    svc.record_application(application(BrokerReportApplicationStatus.DEFERRED))
    with pytest.raises(RecoveryFenceConflictError, match="pending report"):
        svc.finalize(account=ACCOUNT, generation=1, recovery_cut_revision=7, ingress_version=1, recorded_at=NOW)


def test_stale_generation_cut_or_concurrent_ingress_cannot_finalize() -> None:
    repo=Repo(); svc,_=service(repo)
    repo.control=AccountRecoveryControl(broker="SINOPAC", account_ref="A", generation=2, recovery_cut_revision=8, ingress_version=3, active=True, recorded_at=NOW)
    for generation,cut,frontier in ((1,8,3),(2,7,3),(2,8,2)):
        with pytest.raises(RecoveryFenceConflictError): svc.finalize(account=ACCOUNT,generation=generation,recovery_cut_revision=cut,ingress_version=frontier,recorded_at=NOW)


def test_applied_report_allows_race_safe_final_handoff() -> None:
    repo=Repo(); svc,_=service(repo)
    repo.control=AccountRecoveryControl(broker="SINOPAC", account_ref="A", generation=1, recovery_cut_revision=7, ingress_version=0, active=True, recorded_at=NOW)
    svc.capture(entry()); svc.record_application(application())
    result=svc.finalize(account=ACCOUNT,generation=1,recovery_cut_revision=7,ingress_version=1,recorded_at=NOW)
    assert not result.active and not repo.control.active


def test_wrong_generation_ingress_fails_but_post_handoff_capture_is_durable() -> None:
    repo=Repo(); svc,_=service(repo)
    repo.control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=2,recovery_cut_revision=7,ingress_version=0,active=True,recorded_at=NOW)
    with pytest.raises(RecoveryFenceConflictError,match="stale generation"):
        svc.capture(entry(generation=1))
    repo.control=repo.control.model_copy(update={"active":False})
    with pytest.raises(RecoveryFenceConflictError,match="stale generation"):
        svc.capture(entry(generation=1))
    assert svc.capture(entry(ingress_id="IN-2",generation=2)) is BrokerReportIngressStatus.APPENDED
    assert repo.control.ingress_version == 0


def test_application_sequence_must_be_contiguous_and_duplicate_identity_is_stable() -> None:
    repo=Repo(); svc,_=service(repo)
    repo.control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=1,recovery_cut_revision=7,ingress_version=0,active=True,recorded_at=NOW)
    svc.capture(entry())
    first=application(application_id="APP-1",application_sequence=1)
    svc.record_application(first); svc.record_application(first)
    with pytest.raises(BrokerReportConflictError,match="contiguous"):
        svc.record_application(application(application_id="APP-3",application_sequence=3))
    with pytest.raises(BrokerReportConflictError,match="contiguous"):
        svc.record_application(application(application_id="APP-0",application_sequence=1))
    svc.record_application(application(application_id="APP-2",application_sequence=2))


def test_capture_wins_and_stale_frontier_finalize_fails() -> None:
    repo=Repo(); svc,_=service(repo)
    repo.control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=1,recovery_cut_revision=7,ingress_version=0,active=True,recorded_at=NOW)
    svc.capture(entry())
    with pytest.raises(RecoveryFenceConflictError,match="stale fence"):
        svc.finalize(account=ACCOUNT,generation=1,recovery_cut_revision=7,ingress_version=0,recorded_at=NOW)


def test_current_disposition_not_timestamp_or_any_historical_success_controls_handoff() -> None:
    repo=Repo(); svc,_=service(repo)
    repo.control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=1,recovery_cut_revision=7,ingress_version=0,active=True,recorded_at=NOW)
    svc.capture(entry())
    svc.record_application(application(BrokerReportApplicationStatus.APPLIED,application_id="APP-1",application_sequence=1,recorded_at=NOW))
    svc.record_application(application(BrokerReportApplicationStatus.CONFLICT,application_id="APP-2",application_sequence=2,recorded_at=NOW.replace(year=2025)))
    with pytest.raises(RecoveryFenceConflictError,match="pending report"):
        svc.finalize(account=ACCOUNT,generation=1,recovery_cut_revision=7,ingress_version=1,recorded_at=NOW)


def test_later_applied_resolves_deferred_and_duplicate_application_is_idempotent() -> None:
    repo=Repo(); svc,_=service(repo)
    repo.control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=1,recovery_cut_revision=7,ingress_version=0,active=True,recorded_at=NOW)
    svc.capture(entry())
    deferred=application(BrokerReportApplicationStatus.DEFERRED,application_id="APP-1",application_sequence=1)
    svc.record_application(deferred); svc.record_application(deferred)
    svc.record_application(application(BrokerReportApplicationStatus.APPLIED,application_id="APP-2",application_sequence=2))
    assert len(repo.apps)==2
    assert svc.finalize(account=ACCOUNT,generation=1,recovery_cut_revision=7,ingress_version=1,recorded_at=NOW).active is False


def test_wrong_generation_application_and_conflicting_duplicate_fail_closed() -> None:
    repo=Repo(); svc,_=service(repo)
    repo.control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=1,recovery_cut_revision=7,ingress_version=0,active=True,recorded_at=NOW)
    svc.capture(entry())
    with pytest.raises(BrokerReportConflictError,match="generation"):
        svc.record_application(application(generation=2))
    original=application(); svc.record_application(original)
    with pytest.raises(BrokerReportConflictError,match="application conflict"):
        svc.record_application(application(status=BrokerReportApplicationStatus.CONFLICT,application_id=original.application_id))


def test_continuity_reanchor_retains_historical_gap_and_pending_blocks_trust() -> None:
    repo=Repo()
    gap=SequenceGap(gap_id="GAP-1",broker="SINOPAC",account_ref="A",detected_at=NOW,evidence="sequence 10 to 12")
    repo.append_sequence_gap(gap)
    epoch=ExecutionContinuityEpoch(epoch_id="EPOCH-2",broker="SINOPAC",account_ref="A",generation=2,trusted_current=True,historical_degradation=True,anchored_at=NOW,evidence=("verified re-anchor",))
    repo.append_continuity_epoch(epoch)
    assert repo.gaps == [gap] and repo.epochs[0].historical_degradation


def test_continuity_head_is_exact_authority_not_lexical_or_historical_trust() -> None:
    repo=Repo()
    repo.control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=10,recovery_cut_revision=7,ingress_version=0,readiness_revision=0,active=True,recorded_at=NOW)
    old=ExecutionContinuityEpoch(epoch_id="EPOCH-1",broker="SINOPAC",account_ref="A",generation=10,trusted_current=True,historical_degradation=False,anchored_at=NOW,evidence=("old trust",))
    current=ExecutionContinuityEpoch(epoch_id="EPOCH-10",broker="SINOPAC",account_ref="A",generation=10,trusted_current=False,historical_degradation=True,anchored_at=NOW,evidence=("current untrusted",))
    repo.epochs.append(old)
    head=ExecutionContinuityHead(broker="SINOPAC",account_ref="A",generation=10,current_epoch_id="EPOCH-10",transition_receipt_id="TR-1",head_revision=1,readiness_revision=1,recorded_at=NOW)
    receipt=transition_receipt(generation=10,current_epoch_id="EPOCH-10",evidence=("explicit re-anchor",))
    repo.transition_continuity_head(epoch=current,head=head,receipt=receipt,expected_head_revision=0,expected_readiness_revision=0)
    assert repo.head.current_epoch_id == "EPOCH-10"
    assert repo.epochs[0].trusted_current is True
    assert repo.epochs[1].trusted_current is False


def test_continuity_transition_cas_and_duplicate_identity_fail_closed() -> None:
    repo=Repo()
    repo.control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=1,recovery_cut_revision=7,ingress_version=0,readiness_revision=0,active=True,recorded_at=NOW)
    epoch=ExecutionContinuityEpoch(epoch_id="EPOCH-2",broker="SINOPAC",account_ref="A",generation=1,trusted_current=True,historical_degradation=True,anchored_at=NOW,evidence=("re-anchor",))
    head=ExecutionContinuityHead(broker="SINOPAC",account_ref="A",generation=1,current_epoch_id="EPOCH-2",transition_receipt_id="TR-1",head_revision=1,readiness_revision=1,recorded_at=NOW)
    receipt=transition_receipt()
    with pytest.raises(ContinuityAuthorityConflictError,match="conflict"):
        repo.transition_continuity_head(epoch=epoch,head=head,receipt=receipt,expected_head_revision=9,expected_readiness_revision=0)
    repo.transition_continuity_head(epoch=epoch,head=head,receipt=receipt,expected_head_revision=0,expected_readiness_revision=0)
    with pytest.raises(ContinuityAuthorityConflictError,match="conflict"):
        repo.transition_continuity_head(epoch=epoch,head=head,receipt=receipt.model_copy(update={"evidence":("different",)}),expected_head_revision=1,expected_readiness_revision=1)


def test_exact_transition_replay_is_idempotent_even_after_newer_head() -> None:
    repo=Repo(); repo.control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=1,recovery_cut_revision=7,ingress_version=0,readiness_revision=0,active=True,recorded_at=NOW)
    first_epoch=ExecutionContinuityEpoch(epoch_id="EPOCH-2",broker="SINOPAC",account_ref="A",generation=1,trusted_current=True,historical_degradation=False,anchored_at=NOW,evidence=("first",))
    first_head=ExecutionContinuityHead(broker="SINOPAC",account_ref="A",generation=1,current_epoch_id="EPOCH-2",transition_receipt_id="TR-1",head_revision=1,readiness_revision=1,recorded_at=NOW)
    first_receipt=transition_receipt()
    repo.transition_continuity_head(epoch=first_epoch,head=first_head,receipt=first_receipt,expected_head_revision=0,expected_readiness_revision=0)
    second_epoch=first_epoch.model_copy(update={"epoch_id":"EPOCH-3","evidence":("second",)})
    second_head=first_head.model_copy(update={"current_epoch_id":"EPOCH-3","transition_receipt_id":"TR-2","head_revision":2,"readiness_revision":2})
    second_receipt=transition_receipt(transition_id="TR-2",previous_epoch_id="EPOCH-2",current_epoch_id="EPOCH-3",previous_head_revision=1,head_revision=2,previous_readiness_revision=1,readiness_revision=2,evidence_id="EVIDENCE-2")
    repo.transition_continuity_head(epoch=second_epoch,head=second_head,receipt=second_receipt,expected_head_revision=1,expected_readiness_revision=1)
    repo.transition_continuity_head(epoch=first_epoch,head=first_head,receipt=first_receipt,expected_head_revision=0,expected_readiness_revision=0)
    assert repo.head == second_head and repo.control.readiness_revision == 2


@pytest.mark.parametrize("target,updates",[
    ("head",{"current_epoch_id":"OTHER"}),
    ("receipt",{"current_epoch_id":"OTHER"}),
    ("receipt",{"account_ref":"B"}),
    ("receipt",{"generation":2}),
    ("head",{"head_revision":2}),
    ("head",{"transition_receipt_id":"OTHER"}),
])
def test_transition_cross_object_incoherence_fails_closed(target,updates) -> None:
    repo=Repo(); repo.control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=1,recovery_cut_revision=7,ingress_version=0,readiness_revision=0,active=True,recorded_at=NOW)
    epoch=ExecutionContinuityEpoch(epoch_id="EPOCH-2",broker="SINOPAC",account_ref="A",generation=1,trusted_current=True,historical_degradation=False,anchored_at=NOW,evidence=("first",))
    head=ExecutionContinuityHead(broker="SINOPAC",account_ref="A",generation=1,current_epoch_id="EPOCH-2",transition_receipt_id="TR-1",head_revision=1,readiness_revision=1,recorded_at=NOW)
    receipt=transition_receipt()
    if target == "head": head=head.model_copy(update=updates)
    else: receipt=receipt.model_copy(update=updates)
    with pytest.raises(ContinuityAuthorityConflictError,match="coherence"):
        repo.transition_continuity_head(epoch=epoch,head=head,receipt=receipt,expected_head_revision=0,expected_readiness_revision=0)


def test_begin_recovery_requires_fresh_zero_readiness_revision() -> None:
    repo=Repo()
    control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=2,recovery_cut_revision=8,ingress_version=0,readiness_revision=1,active=True,recorded_at=NOW)
    with pytest.raises(RecoveryFenceConflictError,match="zero"):
        repo.begin_recovery(control,expected_generation=1)


def test_readiness_frontier_is_independent_and_inactive_writes_do_not_advance() -> None:
    repo=Repo()
    repo.control=AccountRecoveryControl(broker="SINOPAC",account_ref="A",generation=1,recovery_cut_revision=7,ingress_version=0,readiness_revision=4,active=True,recorded_at=NOW)
    svc,_=service(repo)
    svc.capture(entry())
    assert (repo.control.ingress_version,repo.control.readiness_revision)==(1,5)
    svc.capture(entry())
    assert (repo.control.ingress_version,repo.control.readiness_revision)==(1,5)
    repo.control=repo.control.model_copy(update={"active":False})
    svc.capture(entry(ingress_id="IN-2"))
    assert (repo.control.ingress_version,repo.control.readiness_revision)==(1,5)


def test_models_are_broker_neutral_and_service_has_no_broker_or_account_authority_side_effect() -> None:
    assert "shioaji" not in repr(entry().model_dump()).lower()
    assert not hasattr(BrokerRecoveryEvidenceService, "submit")
    assert not hasattr(BrokerRecoveryEvidenceService, "advance_account_head")
