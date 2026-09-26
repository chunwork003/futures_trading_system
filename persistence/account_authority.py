from __future__ import annotations

from datetime import datetime
from typing import Callable, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from persistence.contracts import (
    PersistenceConflictError,
    UnitOfWork,
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


class AccountAuthorityCommit(BaseModel):
    """Caller-defined material mutation identity and exact expected-state authority target。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    authority_commit_id: str
    mutation_fingerprint: str
    broker: str
    account_ref: str
    expected_head_revision: int = Field(ge=0)
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


@runtime_checkable
class AccountAuthorityParticipant(Protocol):
    """Material participant 只在同一 UoW 內寫入，不得自行 commit 或執行 broker I/O。"""

    def apply(self) -> None: ...


class AccountAuthorityCommitService:
    """Shared atomic account-authority commit primitive。

    它將 material participants、exact checkpoint、revision head 與 stable
    receipt 納入 caller-owned UnitOfWork；不負責 network I/O 或 READY。
    """

    def __init__(
        self,
        *,
        uow_factory: Callable[[], UnitOfWork],
        repository: Callable[[UnitOfWork], AccountAuthorityRepository],
    ) -> None:
        self._uow_factory = uow_factory
        self._repository = repository

    def commit(
        self,
        mutation: AccountAuthorityCommit,
        *,
        participants: tuple[AccountAuthorityParticipant, ...] = (),
    ) -> AccountAuthorityCommitReceipt:
        with self._uow_factory() as uow:
            repository = self._repository(uow)
            existing = repository.get_receipt(mutation.authority_commit_id)
            if existing is not None:
                if (
                    existing.mutation_fingerprint != mutation.mutation_fingerprint
                    or existing.broker != mutation.broker
                    or existing.account_ref != mutation.account_ref
                    or existing.expected_snapshot_id != mutation.expected_snapshot_id
                ):
                    raise AccountAuthorityConflictError(
                        "authority commit identity has conflicting canonical semantics"
                    )
                return existing

            head = repository.lock_head(mutation.broker, mutation.account_ref)
            if head is None:
                raise AccountAuthorityIntegrityError("account authority head is missing")
            if head.current_revision != mutation.expected_head_revision:
                raise AccountAuthorityConflictError("account authority head revision conflict")

            next_revision = mutation.expected_head_revision + 1
            next_head = head.model_copy(
                update={"current_revision": next_revision, "initialized": True}
            )
            checkpoint = AccountRecoveryCheckpoint(
                broker=mutation.broker,
                account_ref=mutation.account_ref,
                account_revision=next_revision,
                expected_snapshot_id=mutation.expected_snapshot_id,
                authority_commit_id=mutation.authority_commit_id,
                recorded_at=mutation.recorded_at,
            )
            receipt = AccountAuthorityCommitReceipt(
                authority_commit_id=mutation.authority_commit_id,
                mutation_fingerprint=mutation.mutation_fingerprint,
                broker=mutation.broker,
                account_ref=mutation.account_ref,
                committed_revision=next_revision,
                expected_snapshot_id=mutation.expected_snapshot_id,
                recorded_at=mutation.recorded_at,
            )

            for participant in participants:
                participant.apply()
            repository.append_checkpoint(checkpoint)
            repository.advance_head(next_head, expected_revision=mutation.expected_head_revision)
            repository.append_receipt(receipt)
            validate_authority_closure(head=next_head, checkpoint=checkpoint, receipt=receipt)
            uow.commit()
            return receipt


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
