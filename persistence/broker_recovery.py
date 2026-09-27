from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Callable, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from persistence.contracts import PersistenceConflictError, UnitOfWork, normalize_aware_utc, normalize_stable_id
from trading.account import BrokerAccount


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
    """Append-only report application history；DEFERRED 保存 post-cut evidence，不直接越過 fence。"""
    model_config = ConfigDict(extra="forbid", frozen=True)
    application_id: str
    ingress_id: str
    generation: int = Field(ge=1)
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
    """Caller-owned UoW 的 recovery evidence/control port；不得成為 economic account authority。"""
    def append_inbox(self, entry: BrokerReportInboxEntry) -> BrokerReportIngressStatus: ...
    def append_application(self, application: BrokerReportApplication) -> None: ...
    def append_sequence_gap(self, gap: SequenceGap) -> None: ...
    def append_continuity_epoch(self, epoch: ExecutionContinuityEpoch) -> None: ...
    def get_control(self, account: BrokerAccount) -> AccountRecoveryControl | None: ...
    def begin_recovery(self, control: AccountRecoveryControl, *, expected_generation: int) -> None: ...
    def finalize_handoff(self, control: AccountRecoveryControl, *, expected_generation: int, expected_ingress_version: int) -> None: ...


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

    def finalize(self, *, account: BrokerAccount, generation: int, recovery_cut_revision: int, ingress_version: int, recorded_at: datetime) -> AccountRecoveryControl:
        with self._uow_factory() as uow:
            repository = self._repository(uow)
            current = repository.get_control(account)
            if current is None or not current.active:
                raise RecoveryFenceConflictError("active recovery control is missing")
            if current.generation != generation or current.recovery_cut_revision != recovery_cut_revision:
                raise RecoveryFenceConflictError("stale recovery generation or cut")
            completed = current.model_copy(update={"active": False, "recorded_at": normalize_aware_utc(recorded_at)})
            repository.finalize_handoff(completed, expected_generation=generation, expected_ingress_version=ingress_version)
            uow.commit()
            return completed


__all__ = ["AccountRecoveryControl", "BrokerRecoveryEvidenceService", "BrokerRecoveryRepository", "BrokerReportApplication", "BrokerReportApplicationStatus", "BrokerReportConflictError", "BrokerReportInboxEntry", "BrokerReportIngressStatus", "ExecutionContinuityEpoch", "RecoveryFenceConflictError", "SequenceGap"]
