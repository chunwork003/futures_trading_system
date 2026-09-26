from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Callable, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from persistence.account_authority import (
    AccountAuthorityCommit,
    AccountAuthorityCommitReceipt,
    AccountAuthorityCommitService,
)
from persistence.contracts import (
    PersistenceConflictError,
    UnitOfWork,
    normalize_aware_utc,
    normalize_stable_id,
)


class BrokerActionKind(str, Enum):
    """V1 會造成 broker material side effect 的 action 種類。"""

    SUBMIT = "SUBMIT"
    CANCEL = "CANCEL"


class BrokerActionResolutionKind(str, Enum):
    """已具 durable evidence 的 action outcome；UNKNOWN 刻意不屬於 resolution。"""

    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    NOT_DISPATCHED = "NOT_DISPATCHED"


class BrokerDispatchOutcome(str, Enum):
    """Injected broker boundary 回報；不等同 OrderStatus 或 retry authority。"""

    DISPATCHED = "DISPATCHED"
    NOT_DISPATCHED = "NOT_DISPATCHED"
    OUTCOME_UNKNOWN = "OUTCOME_UNKNOWN"


class BrokerActionSafetyError(RuntimeError):
    """Broker action 缺少 durable safety authority 時的 fail-closed base error。"""


class BrokerActionConflictError(PersistenceConflictError):
    """同一 BrokerAccount/Order/action 已有 unresolved attempt 或版本衝突。"""


class UnresolvedBrokerActionError(BrokerActionSafetyError):
    """存在 unresolved attempt；禁止 automatic resubmit/recancel。"""


class BrokerActionResolutionError(BrokerActionSafetyError):
    """Resolution 與 durable attempt/head 或 positive proof 不一致。"""


class BrokerActionAttempt(BaseModel):
    """Broker invocation 前必須 durable 的 immutable action evidence。

    authorization_id 只保存 C21 evidence reference；本 model 不授權 production
    activation，也不把 correlation ref 當成 broker server-side idempotency。
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    attempt_id: str
    broker: str
    account_ref: str
    order_id: str
    action: BrokerActionKind
    broker_client_order_ref: str
    command_id: str
    correlation_id: str
    authorization_id: str
    created_at: datetime

    @field_validator(
        "attempt_id", "account_ref", "order_id", "broker_client_order_ref",
        "command_id", "correlation_id", "authorization_id", mode="before",
    )
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("broker", mode="before")
    @classmethod
    def _broker(cls, value: object) -> object:
        return normalize_stable_id(value).upper() if isinstance(value, str) else value

    @field_validator("created_at")
    @classmethod
    def _created_at(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)


class BrokerActionResolution(BaseModel):
    """Immutable known outcome evidence；NOT_DISPATCHED 必須有 verified pre-transport proof。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    resolution_id: str
    attempt_id: str
    kind: BrokerActionResolutionKind
    evidence: tuple[str, ...]
    resolved_at: datetime
    pre_transport_proof: str | None = None

    @field_validator("resolution_id", "attempt_id", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("evidence", mode="before")
    @classmethod
    def _evidence(cls, value: object) -> object:
        if not isinstance(value, (tuple, list)):
            return value
        return tuple(normalize_stable_id(item) for item in value)

    @field_validator("pre_transport_proof", mode="before")
    @classmethod
    def _proof(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("resolved_at")
    @classmethod
    def _resolved_at(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)

    @model_validator(mode="after")
    def _proof_invariant(self) -> "BrokerActionResolution":
        if not self.evidence:
            raise ValueError("broker action resolution requires evidence")
        if self.kind is BrokerActionResolutionKind.NOT_DISPATCHED:
            if self.pre_transport_proof is None:
                raise ValueError("NOT_DISPATCHED requires verified pre-transport proof")
        elif self.pre_transport_proof is not None:
            raise ValueError("pre-transport proof is only valid for NOT_DISPATCHED")
        return self


class BrokerActionHead(BaseModel):
    """每個 account/order/action scope 的 durable concurrency projection。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    broker: str
    account_ref: str
    order_id: str
    action: BrokerActionKind
    version: int = Field(ge=0)
    unresolved_attempt_id: str | None = None

    @field_validator("account_ref", "order_id", "unresolved_attempt_id", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("broker", mode="before")
    @classmethod
    def _broker(cls, value: object) -> object:
        return normalize_stable_id(value).upper() if isinstance(value, str) else value


class BrokerInvocationResult(BaseModel):
    """Broker port 的 typed dispatch observation；只有 positive proof 可稱 NOT_DISPATCHED。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    outcome: BrokerDispatchOutcome
    evidence: str
    pre_transport_proof: str | None = None

    @field_validator("evidence", "pre_transport_proof", mode="before")
    @classmethod
    def _text(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @model_validator(mode="after")
    def _dispatch_invariant(self) -> "BrokerInvocationResult":
        if self.outcome is BrokerDispatchOutcome.NOT_DISPATCHED:
            if self.pre_transport_proof is None:
                raise ValueError("NOT_DISPATCHED requires positive pre-transport proof")
        elif self.pre_transport_proof is not None:
            raise ValueError("pre-transport proof only applies to NOT_DISPATCHED")
        return self


@runtime_checkable
class BrokerActionRepository(Protocol):
    """Caller-owned UoW 內的 durable action evidence port；不得自行 commit。"""

    def get_attempt(self, attempt_id: str) -> BrokerActionAttempt | None: ...
    def append_attempt(self, attempt: BrokerActionAttempt) -> None: ...
    def get_head(
        self, broker: str, account_ref: str, order_id: str, action: BrokerActionKind
    ) -> BrokerActionHead | None: ...
    def reserve_head(self, attempt: BrokerActionAttempt, *, expected_version: int) -> None: ...
    def append_resolution(self, resolution: BrokerActionResolution) -> None: ...
    def release_head(
        self, attempt: BrokerActionAttempt, *, expected_version: int
    ) -> None: ...


class BrokerActionAttemptParticipant:
    """在 AccountAuthorityCommit transaction 中原子 reserve head 與 append attempt。"""

    def __init__(self, repository: BrokerActionRepository, attempt: BrokerActionAttempt) -> None:
        self._repository = repository
        self._attempt = attempt
        self.applied = False

    def apply(self) -> None:
        head = self._repository.get_head(
            self._attempt.broker, self._attempt.account_ref,
            self._attempt.order_id, self._attempt.action,
        )
        if head is not None and head.unresolved_attempt_id is not None:
            raise UnresolvedBrokerActionError(
                f"unresolved {self._attempt.action.value} attempt blocks invocation"
            )
        expected_version = -1 if head is None else head.version
        self._repository.append_attempt(self._attempt)
        self._repository.reserve_head(self._attempt, expected_version=expected_version)
        self.applied = True


class BrokerActionResolutionParticipant:
    """Known resolution 與 head release 的同 transaction participant。"""

    def __init__(
        self,
        repository: BrokerActionRepository,
        attempt: BrokerActionAttempt,
        resolution: BrokerActionResolution,
    ) -> None:
        self._repository = repository
        self._attempt = attempt
        self._resolution = resolution

    def apply(self) -> None:
        if self._resolution.attempt_id != self._attempt.attempt_id:
            raise BrokerActionResolutionError("resolution attempt identity mismatch")
        head = self._repository.get_head(
            self._attempt.broker, self._attempt.account_ref,
            self._attempt.order_id, self._attempt.action,
        )
        if head is None or head.unresolved_attempt_id != self._attempt.attempt_id:
            raise BrokerActionResolutionError("attempt is not the unresolved action head")
        self._repository.append_resolution(self._resolution)
        self._repository.release_head(self._attempt, expected_version=head.version)


T = TypeVar("T")


class BrokerActionSafetyService:
    """先 durable attempt，再於 UoW 結束後呼叫 injected broker boundary。

    本 service 不推論 timeout、zero-match 或 correlation ref 為 retry authority；
    unknown outcome 保持 unresolved，且不提供 manual override。
    """

    def __init__(
        self,
        *,
        authority_service: AccountAuthorityCommitService,
        repository: Callable[[UnitOfWork], BrokerActionRepository],
    ) -> None:
        self._authority_service = authority_service
        self._repository = repository

    def commit_attempt_then_invoke(
        self,
        *,
        mutation: AccountAuthorityCommit,
        attempt: BrokerActionAttempt,
        invoke: Callable[[BrokerActionAttempt], T],
    ) -> tuple[AccountAuthorityCommitReceipt, T]:
        holder: list[BrokerActionAttemptParticipant] = []

        def participants(uow: UnitOfWork):
            participant = BrokerActionAttemptParticipant(self._repository(uow), attempt)
            holder.append(participant)
            return (participant,)

        receipt = self._authority_service.commit(
            mutation, participant_factory=participants
        )
        if not holder or not holder[0].applied:
            raise UnresolvedBrokerActionError(
                "durable attempt already exists; automatic broker re-invocation is forbidden"
            )
        return receipt, invoke(attempt)

    def commit_resolution(
        self,
        *,
        mutation: AccountAuthorityCommit,
        attempt: BrokerActionAttempt,
        resolution: BrokerActionResolution,
    ) -> AccountAuthorityCommitReceipt:
        def participants(uow: UnitOfWork):
            return (
                BrokerActionResolutionParticipant(
                    self._repository(uow), attempt, resolution
                ),
            )

        return self._authority_service.commit(
            mutation, participant_factory=participants
        )


__all__ = [
    "BrokerActionAttempt", "BrokerActionConflictError", "BrokerActionHead",
    "BrokerActionKind", "BrokerActionRepository", "BrokerActionResolution",
    "BrokerActionResolutionError", "BrokerActionResolutionKind",
    "BrokerActionSafetyError", "BrokerActionSafetyService", "BrokerDispatchOutcome",
    "BrokerInvocationResult", "UnresolvedBrokerActionError",
]
