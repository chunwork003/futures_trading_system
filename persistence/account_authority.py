from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from persistence.contracts import (
    PersistenceConflictError,
    normalize_aware_utc,
    normalize_stable_id,
)


class AccountAuthorityIntegrityError(RuntimeError):
    """BrokerAccount authority head/checkpoint/receipt 無法形成完整閉包時 fail closed。"""


class AccountAuthorityConflictError(PersistenceConflictError):
    """Account revision 或 stable commit identity 與 durable authority 衝突。"""


class AccountStateHead(BaseModel):
    """BrokerAccount 的 material authority frontier；不是 READY 或 broker currentness。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    broker: str
    account_ref: str
    current_revision: int = Field(ge=0)
    initialized: bool = False

    @field_validator("broker", mode="before")
    @classmethod
    def _broker(cls, value: object) -> object:
        return normalize_stable_id(value).upper() if isinstance(value, str) else value

    @field_validator("account_ref", mode="before")
    @classmethod
    def _account_ref(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @model_validator(mode="after")
    def _revision_state(self) -> "AccountStateHead":
        if self.initialized != (self.current_revision >= 1):
            raise ValueError("initialized authority requires revision >= 1")
        return self


class AccountRecoveryCheckpoint(BaseModel):
    """Material revision 的 exact recovery checkpoint；禁止以 latest snapshot 代替。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    broker: str
    account_ref: str
    account_revision: int = Field(ge=1)
    expected_snapshot_id: str
    authority_commit_id: str
    recorded_at: datetime

    @field_validator("broker", mode="before")
    @classmethod
    def _broker(cls, value: object) -> object:
        return normalize_stable_id(value).upper() if isinstance(value, str) else value

    @field_validator("account_ref", "expected_snapshot_id", "authority_commit_id", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("recorded_at")
    @classmethod
    def _recorded_at(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)


class AccountAuthorityCommitReceipt(BaseModel):
    """Stable authority commit 的 durable receipt；用於 retry 辨識相同或衝突語意。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    authority_commit_id: str
    mutation_fingerprint: str
    broker: str
    account_ref: str
    committed_revision: int = Field(ge=1)
    expected_snapshot_id: str
    recorded_at: datetime

    @field_validator(
        "authority_commit_id",
        "mutation_fingerprint",
        "account_ref",
        "expected_snapshot_id",
        mode="before",
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
    def _recorded_at(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)


@runtime_checkable
class AccountAuthorityRepository(Protocol):
    """Caller-owned transaction 內的 account authority persistence port。"""

    def lock_head(self, broker: str, account_ref: str) -> AccountStateHead | None: ...
    def advance_head(self, head: AccountStateHead, *, expected_revision: int) -> None: ...
    def append_checkpoint(self, checkpoint: AccountRecoveryCheckpoint) -> None: ...
    def get_checkpoint(self, broker: str, account_ref: str, account_revision: int) -> AccountRecoveryCheckpoint | None: ...
    def append_receipt(self, receipt: AccountAuthorityCommitReceipt) -> None: ...
    def get_receipt(self, authority_commit_id: str) -> AccountAuthorityCommitReceipt | None: ...


def validate_authority_closure(
    *,
    head: AccountStateHead,
    checkpoint: AccountRecoveryCheckpoint,
    receipt: AccountAuthorityCommitReceipt,
) -> None:
    """驗證 head/checkpoint/receipt 的 exact account/revision/snapshot closure。"""

    scopes = {
        (head.broker, head.account_ref),
        (checkpoint.broker, checkpoint.account_ref),
        (receipt.broker, receipt.account_ref),
    }
    if len(scopes) != 1:
        raise AccountAuthorityIntegrityError("account authority scope mismatch")
    if not head.initialized or head.current_revision != checkpoint.account_revision:
        raise AccountAuthorityIntegrityError("checkpoint does not match account revision head")
    if receipt.committed_revision != checkpoint.account_revision:
        raise AccountAuthorityIntegrityError("receipt does not match checkpoint revision")
    if receipt.authority_commit_id != checkpoint.authority_commit_id:
        raise AccountAuthorityIntegrityError("receipt does not match authority commit identity")
    if receipt.expected_snapshot_id != checkpoint.expected_snapshot_id:
        raise AccountAuthorityIntegrityError("receipt does not match exact expected snapshot")
