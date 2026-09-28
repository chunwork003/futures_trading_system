from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Callable, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from persistence.contracts import PersistenceConflictError, PersistenceContractError, UnitOfWork, normalize_aware_utc, normalize_stable_id
from persistence.account import AccountPositionSnapshot
from persistence.account_authority import AccountAuthorityCommit, AccountAuthorityCommitReceipt, AccountAuthorityCommitService, AccountAuthorityParticipant
from persistence.execution import ExecutionPersistenceService, FillRepository
from trading.account import BrokerAccount
from trading.broker_recovery import (
    BrokerDealEvidence,
    BrokerDealSetCompleteness,
    BrokerLifecycleEvidence,
    reconstruct_broker_order,
)
from trading.execution import Order, OrderEvent, OrderEventProvenance


class BrokerReportIngressStatus(str, Enum):
    """Immutable broker report ingress 的 append 結果。"""
    APPENDED = "APPENDED"
    DUPLICATE = "DUPLICATE"


class BrokerReportApplicationStatus(str, Enum):
    """Inbox evidence 的 immutable application classification。"""
    APPLIED = "APPLIED"
    DUPLICATE = "DUPLICATE"
    CORROBORATED = "CORROBORATED"
    DEFERRED = "DEFERRED"
    CONFLICT = "CONFLICT"


class BrokerReportConflictError(PersistenceConflictError):
    """相同 ingress identity 對應不同 material content 時 fail closed。"""


class RecoveryFenceConflictError(PersistenceConflictError):
    """Recovery generation、cut 或 ingress frontier stale 時拒絕 handoff。"""


class ContinuityAuthorityConflictError(PersistenceConflictError):
    """Continuity head、transition identity 或 readiness CAS 不一致時 fail closed。"""


class BrokerReportInboxEntry(BaseModel):
    """Broker-neutral durable ingress evidence；capture 本身不推進 AccountStateHead。"""
    model_config = ConfigDict(extra="forbid", frozen=True)
    ingress_id: str
    broker: str
    account_ref: str
    generation: int = Field(ge=1)
    received_at: datetime
    report_type: str
    payload_fingerprint: str
    payload_json: dict[str, object]

    @field_validator("ingress_id", "account_ref", "report_type", "payload_fingerprint", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("broker", mode="before")
    @classmethod
    def _broker(cls, value: object) -> object:
        return normalize_stable_id(value).upper() if isinstance(value, str) else value

    @field_validator("received_at")
    @classmethod
    def _time(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)


class BrokerReportApplication(BaseModel):
    """Append-only application history；repository 以連續 sequence 序列化 current disposition，時間不是 authority。"""
    model_config = ConfigDict(extra="forbid", frozen=True)
    application_id: str
    ingress_id: str
    generation: int = Field(ge=1)
    application_sequence: int = Field(ge=1)
    status: BrokerReportApplicationStatus
    recorded_at: datetime
    evidence: tuple[str, ...]

    @field_validator("application_id", "ingress_id", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("recorded_at")
    @classmethod
    def _time(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)

    @field_validator("evidence", mode="before")
    @classmethod
    def _evidence(cls, value: object) -> object:
        return tuple(normalize_stable_id(v) for v in value) if isinstance(value, (tuple, list)) else value

    @model_validator(mode="after")
    def _nonempty(self) -> "BrokerReportApplication":
        if not self.evidence:
            raise ValueError("broker report application requires evidence")
        return self


class AccountRecoveryControl(BaseModel):
    """與 AccountStateHead 分離的 short-fence generation/control；不是完整 C12 RecoveryCut。"""
    model_config = ConfigDict(extra="forbid", frozen=True)
    broker: str
    account_ref: str
    generation: int = Field(ge=1)
    recovery_cut_revision: int = Field(ge=0)
    ingress_version: int = Field(ge=0)
    readiness_revision: int = Field(default=0, ge=0)
    active: bool
    recorded_at: datetime

    @field_validator("account_ref", mode="before")
    @classmethod
    def _account(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("broker", mode="before")
    @classmethod
    def _broker(cls, value: object) -> object:
        return normalize_stable_id(value).upper() if isinstance(value, str) else value

    @field_validator("recorded_at")
    @classmethod
    def _time(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)


class ExecutionContinuityEpoch(BaseModel):
    """Current trust 與 historical degradation 分離的 durable continuity evidence。"""
    model_config = ConfigDict(extra="forbid", frozen=True)
    epoch_id: str
    broker: str
    account_ref: str
    generation: int = Field(ge=1)
    trusted_current: bool
    historical_degradation: bool
    anchored_at: datetime
    evidence: tuple[str, ...]

    @field_validator("epoch_id", "account_ref", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("broker", mode="before")
    @classmethod
    def _broker(cls, value: object) -> object:
        return normalize_stable_id(value).upper() if isinstance(value, str) else value

    @field_validator("anchored_at")
    @classmethod
    def _time(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)


class ExecutionContinuityHead(BaseModel):
    """BrokerAccount 唯一 current continuity selector；epoch 自身旗標不具 current authority。"""
    model_config = ConfigDict(extra="forbid", frozen=True)
    broker: str
    account_ref: str
    generation: int = Field(ge=1)
    current_epoch_id: str
    transition_receipt_id: str
    head_revision: int = Field(ge=1)
    readiness_revision: int = Field(ge=1)
    recorded_at: datetime

    @field_validator("account_ref", "current_epoch_id", "transition_receipt_id", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("broker", mode="before")
    @classmethod
    def _broker(cls, value: object) -> object:
        return normalize_stable_id(value).upper() if isinstance(value, str) else value

    @field_validator("recorded_at")
    @classmethod
    def _time(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)


class ContinuityTransitionReceipt(BaseModel):
    """Append-only continuity transition 證據；revision 鏈而非時間決定 currentness。"""
    model_config = ConfigDict(extra="forbid", frozen=True)
    transition_id: str
    broker: str
    account_ref: str
    generation: int = Field(ge=1)
    previous_epoch_id: str | None
    current_epoch_id: str
    previous_head_revision: int = Field(ge=0)
    head_revision: int = Field(ge=1)
    previous_readiness_revision: int = Field(ge=0)
    readiness_revision: int = Field(ge=1)
    recovery_cut_fingerprint: str
    anchor_fingerprint: str
    ingress_version: int = Field(ge=0)
    account_revision: int = Field(ge=0)
    expected_snapshot_id: str
    authority_commit_id: str
    gap_set_fingerprint: str
    producer_id: str
    contract_version: str
    evidence_id: str
    recorded_at: datetime
    evidence: tuple[str, ...]

    @field_validator(
        "transition_id", "account_ref", "previous_epoch_id", "current_epoch_id",
        "recovery_cut_fingerprint", "anchor_fingerprint", "expected_snapshot_id",
        "authority_commit_id", "gap_set_fingerprint", "producer_id",
        "contract_version", "evidence_id", mode="before",
    )
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("broker", mode="before")
    @classmethod
    def _broker(cls, value: object) -> object:
        return normalize_stable_id(value).upper() if isinstance(value, str) else value

    @field_validator("recorded_at")
    @classmethod
    def _time(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)

    @field_validator("evidence", mode="before")
    @classmethod
    def _evidence(cls, value: object) -> object:
        return tuple(normalize_stable_id(v) for v in value) if isinstance(value, (tuple, list)) else value

    @model_validator(mode="after")
    def _chain(self) -> "ContinuityTransitionReceipt":
        if self.head_revision != self.previous_head_revision + 1:
            raise ValueError("continuity head revision must be contiguous")
        if self.readiness_revision != self.previous_readiness_revision + 1:
            raise ValueError("readiness revision must be contiguous")
        if not self.evidence:
            raise ValueError("continuity transition requires evidence")
        return self


class SequenceGap(BaseModel):
    """Append-only historical stream degradation；re-anchor 不得刪除或改寫。"""
    model_config = ConfigDict(extra="forbid", frozen=True)
    gap_id: str
    broker: str
    account_ref: str
    detected_at: datetime
    evidence: str

    @field_validator("gap_id", "account_ref", "evidence", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("broker", mode="before")
    @classmethod
    def _broker(cls, value: object) -> object:
        return normalize_stable_id(value).upper() if isinstance(value, str) else value

    @field_validator("detected_at")
    @classmethod
    def _time(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)


@runtime_checkable
class BrokerRecoveryRepository(Protocol):
    """Caller-owned UoW 的 recovery evidence/control port；ingress 與 handoff 共用 durable fence。"""
    def append_inbox(self, entry: BrokerReportInboxEntry) -> BrokerReportIngressStatus: ...
    def append_application(self, application: BrokerReportApplication) -> None: ...
    def append_sequence_gap(self, gap: SequenceGap) -> None: ...
    def append_continuity_epoch(self, epoch: ExecutionContinuityEpoch) -> None: ...
    def transition_continuity_head(self, *, epoch: ExecutionContinuityEpoch, head: ExecutionContinuityHead, receipt: ContinuityTransitionReceipt, expected_head_revision: int, expected_readiness_revision: int) -> None: ...
    def get_control(self, account: BrokerAccount) -> AccountRecoveryControl | None: ...
    def begin_recovery(self, control: AccountRecoveryControl, *, expected_generation: int) -> None: ...
    def finalize_handoff(self, control: AccountRecoveryControl, *, expected_generation: int, expected_ingress_version: int, expected_readiness_revision: int) -> None: ...


class BrokerRecoveryEvidenceService:
    """以 caller-owned transaction capture inbox 與 control；不呼叫 broker、不推進 AccountStateHead。"""
    def __init__(self, *, uow_factory: Callable[[], UnitOfWork], repository: Callable[[UnitOfWork], BrokerRecoveryRepository]) -> None:
        self._uow_factory, self._repository = uow_factory, repository

    def capture(self, entry: BrokerReportInboxEntry) -> BrokerReportIngressStatus:
        with self._uow_factory() as uow:
            status = self._repository(uow).append_inbox(entry)
            uow.commit()
            return status

    def record_application(self, application: BrokerReportApplication) -> None:
        with self._uow_factory() as uow:
            self._repository(uow).append_application(application)
            uow.commit()

    def transition_continuity(self, *, epoch: ExecutionContinuityEpoch, head: ExecutionContinuityHead, receipt: ContinuityTransitionReceipt, expected_head_revision: int, expected_readiness_revision: int) -> None:
        """在 caller-owned transaction 以 head/readiness 雙 CAS 切換唯一 current epoch。"""
        with self._uow_factory() as uow:
            self._repository(uow).transition_continuity_head(epoch=epoch, head=head, receipt=receipt, expected_head_revision=expected_head_revision, expected_readiness_revision=expected_readiness_revision)
            uow.commit()

    def finalize(self, *, account: BrokerAccount, generation: int, recovery_cut_revision: int, ingress_version: int, recorded_at: datetime) -> AccountRecoveryControl:
        with self._uow_factory() as uow:
            repository = self._repository(uow)
            current = repository.get_control(account)
            if current is None or not current.active:
                raise RecoveryFenceConflictError("active recovery control is missing")
            if current.generation != generation or current.recovery_cut_revision != recovery_cut_revision:
                raise RecoveryFenceConflictError("stale recovery generation or cut")
            completed = current.model_copy(update={"active": False, "recorded_at": normalize_aware_utc(recorded_at)})
            repository.finalize_handoff(completed, expected_generation=generation, expected_ingress_version=ingress_version, expected_readiness_revision=current.readiness_revision)
            uow.commit()
            return completed


class BrokerRecoveryExecutionService:
    """以唯一 AccountAuthorityCommit 原子接受 recovery execution material。

    上游只能提供已驗證 broker-neutral deal evidence；本 service 先讀完整
    canonical Fill set，再將 OrderEvent、Fill、projection、expected snapshot 與
    可選 BrokerAction resolution participants 放入同一 UoW。它不呼叫 broker。
    """
    def __init__(
        self,
        *,
        authority_service: AccountAuthorityCommitService,
        execution_service: ExecutionPersistenceService,
        fill_repository: Callable[[UnitOfWork], FillRepository],
    ) -> None:
        self._authority_service = authority_service
        self._execution_service = execution_service
        self._fill_repository = fill_repository

    def commit(
        self,
        *,
        mutation: AccountAuthorityCommit,
        previous_event: OrderEvent,
        event: OrderEvent,
        order: Order,
        expected_version: int,
        evidence: tuple[BrokerDealEvidence, ...],
        deal_set_completeness: BrokerDealSetCompleteness,
        lifecycle_evidence: BrokerLifecycleEvidence | None,
        expected_snapshot: AccountPositionSnapshot | None,
        prior_expected_snapshot_id: str,
        additional_participants: Callable[[UnitOfWork], tuple[AccountAuthorityParticipant, ...]] | None = None,
    ) -> AccountAuthorityCommitReceipt:
        def participants(uow: UnitOfWork) -> tuple[AccountAuthorityParticipant, ...]:
            repository = self._fill_repository(uow)
            local_fills = repository.list_by_order(order.order_id)
            plan = reconstruct_broker_order(
                order=order.model_copy(update={"status": previous_event.status}),
                local_fills=local_fills,
                evidence=evidence,
                event_id=event.event_id,
                correlation_id=event.correlation_id,
                authority_broker=mutation.broker,
                authority_account_ref=mutation.account_ref,
                deal_set_completeness=deal_set_completeness,
                lifecycle_evidence=lifecycle_evidence,
            )
            if not plan.material_change:
                raise PersistenceContractError("recovery evidence produces no material lifecycle or Fill change")
            if event.provenance not in {
                OrderEventProvenance.BROKER_CALLBACK,
                OrderEventProvenance.BROKER_DISCOVERY,
            }:
                raise PersistenceContractError("broker recovery event requires broker provenance")
            if event.status is not plan.status:
                raise PersistenceContractError("OrderEvent status does not match reconstructed Fill set")
            if (
                order.status is not plan.status
                or order.filled_quantity != plan.filled_quantity
                or order.average_fill_price != plan.average_fill_price
            ):
                raise PersistenceContractError("Order projection economics do not match canonical Fill set")
            if plan.accepted_fills:
                if expected_snapshot is None:
                    raise PersistenceContractError("position-changing recovery requires complete expected snapshot")
                if mutation.expected_snapshot_id != expected_snapshot.snapshot_id:
                    raise PersistenceContractError("authority checkpoint must reference recovery snapshot")
            elif mutation.expected_snapshot_id != prior_expected_snapshot_id:
                raise PersistenceContractError("status-only recovery must carry forward expected snapshot")
            execution = self._execution_service.participant(
                uow=uow,
                event=event,
                previous_event=previous_event,
                fills=plan.accepted_fills,
                order=order,
                expected_version=expected_version,
                expected_snapshot=expected_snapshot,
            )
            extras = () if additional_participants is None else additional_participants(uow)
            return (execution,) + extras

        return self._authority_service.commit(mutation, participant_factory=participants)


__all__ = ["AccountRecoveryControl", "BrokerRecoveryEvidenceService", "BrokerRecoveryExecutionService", "BrokerRecoveryRepository", "BrokerReportApplication", "BrokerReportApplicationStatus", "BrokerReportConflictError", "BrokerReportInboxEntry", "BrokerReportIngressStatus", "ExecutionContinuityEpoch", "RecoveryFenceConflictError", "SequenceGap"]
