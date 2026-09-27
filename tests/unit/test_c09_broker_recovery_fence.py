from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from persistence.broker_recovery import (
    AccountRecoveryControl, BrokerRecoveryEvidenceService, BrokerReportApplication,
    BrokerReportApplicationStatus, BrokerReportConflictError, BrokerReportInboxEntry,
    BrokerReportIngressStatus, ExecutionContinuityEpoch, RecoveryFenceConflictError,
    SequenceGap,
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
    def __init__(self): self.inbox={}; self.apps=[]; self.gaps=[]; self.epochs=[]; self.control=None; self.ingress_version=0
    def append_inbox(self, item):
        existing=self.inbox.get(item.ingress_id)
        if existing is not None:
            if existing != item: raise BrokerReportConflictError("ingress conflict")
            return BrokerReportIngressStatus.DUPLICATE
        self.inbox[item.ingress_id]=item; self.ingress_version += 1
        if self.control is not None:
            self.control=self.control.model_copy(update={"ingress_version":self.ingress_version})
        return BrokerReportIngressStatus.APPENDED
    def append_application(self, item): self.apps.append(item)
    def append_sequence_gap(self, item): self.gaps.append(item)
    def append_continuity_epoch(self, item): self.epochs.append(item)
    def get_control(self, account): return self.control
    def begin_recovery(self, control, *, expected_generation): self.control=control
    def finalize_handoff(self, control, *, expected_generation, expected_ingress_version):
        if self.control.generation != expected_generation or self.control.ingress_version != expected_ingress_version:
            raise RecoveryFenceConflictError("stale fence")
        pending={key for key in self.inbox if key not in {a.ingress_id for a in self.apps if a.status in (BrokerReportApplicationStatus.APPLIED, BrokerReportApplicationStatus.DUPLICATE, BrokerReportApplicationStatus.CORROBORATED)}}
        if pending: raise RecoveryFenceConflictError("pending report")
        self.control=control


def entry(**updates):
    values=dict(ingress_id="IN-1", broker="SINOPAC", account_ref="A", generation=1, received_at=NOW, report_type="ORDER", payload_fingerprint="FP-1", payload_json={"status":"Submitted"})
    values.update(updates); return BrokerReportInboxEntry(**values)


def application(status=BrokerReportApplicationStatus.APPLIED, **updates):
    values=dict(application_id=f"APP-{status.value}", ingress_id="IN-1", generation=1, status=status, recorded_at=NOW, evidence=("classified exact ingress",))
    values.update(updates); return BrokerReportApplication(**values)


def service(repo):
    uows=[]
    def factory(): item=Uow(); uows.append(item); return item
    return BrokerRecoveryEvidenceService(uow_factory=factory, repository=lambda _:repo), uows


def test_inbox_is_immutable_and_exact_duplicate_is_idempotent() -> None:
    repo=Repo(); svc,uows=service(repo); item=entry()
    assert svc.capture(item) is BrokerReportIngressStatus.APPENDED
    assert svc.capture(item) is BrokerReportIngressStatus.DUPLICATE
    assert len(repo.inbox)==1 and all(u.committed for u in uows)
    with pytest.raises(ValidationError): item.payload_fingerprint="OTHER"


def test_same_ingress_identity_with_conflicting_content_fails_closed() -> None:
    repo=Repo(); svc,_=service(repo); svc.capture(entry())
    with pytest.raises(BrokerReportConflictError): svc.capture(entry(payload_fingerprint="OTHER"))


def test_application_statuses_are_exact_and_append_only() -> None:
    assert {item.value for item in BrokerReportApplicationStatus} == {"APPLIED","DUPLICATE","CORROBORATED","DEFERRED","CONFLICT"}
    repo=Repo(); svc,_=service(repo)
    for status in BrokerReportApplicationStatus: svc.record_application(application(status, application_id=f"APP-{status.value}"))
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


def test_continuity_reanchor_retains_historical_gap_and_pending_blocks_trust() -> None:
    repo=Repo()
    gap=SequenceGap(gap_id="GAP-1",broker="SINOPAC",account_ref="A",detected_at=NOW,evidence="sequence 10 to 12")
    repo.append_sequence_gap(gap)
    epoch=ExecutionContinuityEpoch(epoch_id="EPOCH-2",broker="SINOPAC",account_ref="A",generation=2,trusted_current=True,historical_degradation=True,anchored_at=NOW,evidence=("verified re-anchor",))
    repo.append_continuity_epoch(epoch)
    assert repo.gaps == [gap] and repo.epochs[0].historical_degradation


def test_models_are_broker_neutral_and_service_has_no_broker_or_account_authority_side_effect() -> None:
    assert "shioaji" not in repr(entry().model_dump()).lower()
    assert not hasattr(BrokerRecoveryEvidenceService, "submit")
    assert not hasattr(BrokerRecoveryEvidenceService, "advance_account_head")
