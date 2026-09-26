from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Callable, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from persistence.contracts import (
    PersistenceConflictError,
    UnitOfWork,
    normalize_aware_utc,
    normalize_stable_id,
)
from persistence.account import (
    AccountPositionSnapshot,
    BrokerPositionObservation,
    BrokerPositionObservationRepository,
    ExpectedPositionSnapshotRepository,
)
from persistence.events import EventAppendStatus, EventLedgerRepository, TradingEvent
from trading.account import AccountPosition
from trading.authorization import (
    AuthorizationEnvironment,
    ProtectedActionAuthorization,
    ProtectedActionAuthorizationProvider,
    require_protected_action_authorization,
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
        participant_factory: Callable[[UnitOfWork], tuple[AccountAuthorityParticipant, ...]] | None = None,
        initialization: bool = False,
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
            if mutation.expected_head_revision == 0 and not initialization:
                raise AccountAuthorityIntegrityError(
                    "revision-zero authority transition requires explicit initialization"
                )
            if initialization and mutation.expected_head_revision != 0:
                raise AccountAuthorityConflictError(
                    "initialization requires the reserved revision-zero authority head"
                )

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

            material_participants = participants + (
                () if participant_factory is None else participant_factory(uow)
            )
            for participant in material_participants:
                participant.apply()
            repository.append_checkpoint(checkpoint)
            repository.advance_head(next_head, expected_revision=mutation.expected_head_revision)
            repository.append_receipt(receipt)
            validate_authority_closure(head=next_head, checkpoint=checkpoint, receipt=receipt)
            uow.commit()
            return receipt


class ExpectedStateInitializationMode(str, Enum):
    """Expected-state authority 的唯一初始化模式集合。"""

    FLAT = "FLAT"
    BROKER_SEED = "BROKER_SEED"


class ExpectedStateInitializationError(RuntimeError):
    """Initialization 缺少完整 evidence、currentness 或 authority 時 fail closed。"""


class InitializationCurrentnessEvidence(BaseModel):
    """Broker observation 已通過指定環境 currentness gate 的 typed evidence。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    evidence_id: str
    protected_world_fingerprint: str
    environment: AuthorizationEnvironment

    @field_validator("evidence_id", "protected_world_fingerprint", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value


@runtime_checkable
class InitializationCurrentnessProvider(Protocol):
    @property
    def environment(self) -> AuthorizationEnvironment: ...
    def verify(self, protected_world_fingerprint: str) -> InitializationCurrentnessEvidence | None: ...


class ExpectedStateInitializationRequest(BaseModel):
    """Caller-supplied deterministic initialization command；不含 broker I/O 或 hidden clock。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    event_id: str
    snapshot_id: str
    authority_commit_id: str
    mutation_fingerprint: str
    mode: ExpectedStateInitializationMode
    observation: BrokerPositionObservation
    seeded_positions: tuple[AccountPosition, ...]
    confirmed_by: str
    confirmed_at: datetime
    reason: str | None = None
    authorization_id: str
    command_id: str
    correlation_id: str
    protected_world_fingerprint: str
    environment: AuthorizationEnvironment

    @field_validator(
        "event_id", "snapshot_id", "authority_commit_id", "mutation_fingerprint",
        "confirmed_by", "authorization_id", "command_id", "correlation_id",
        "protected_world_fingerprint", mode="before",
    )
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("confirmed_at")
    @classmethod
    def _confirmed_at(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)

    @field_validator("reason", mode="before")
    @classmethod
    def _reason(cls, value: object) -> object:
        if value is None:
            return None
        return normalize_stable_id(value) if isinstance(value, str) else value

    @model_validator(mode="after")
    def _mode_invariants(self) -> "ExpectedStateInitializationRequest":
        if self.mode is ExpectedStateInitializationMode.FLAT:
            if self.seeded_positions or self.observation.positions:
                raise ValueError("FLAT initialization requires empty complete positions")
        else:
            if not self.seeded_positions or not self.observation.positions:
                raise ValueError("BROKER_SEED initialization requires non-empty positions")
            if self.reason is None:
                raise ValueError("BROKER_SEED initialization requires reason")
            observed = tuple(
                (p.instrument_id, p.contract_id, p.direction, p.quantity)
                for p in self.observation.positions
            )
            seeded = tuple(
                (p.instrument_id, p.contract_id, p.direction, p.quantity)
                for p in self.seeded_positions
            )
            if seeded != observed:
                raise ValueError("BROKER_SEED positions must derive exactly from observation")
        if any(
            p.broker != self.observation.broker
            or p.account_ref != self.observation.account_ref
            for p in self.seeded_positions
        ):
            raise ValueError("seeded positions must match observation account scope")
        return self


class _Apply:
    def __init__(self, operation: Callable[[], None]) -> None:
        self._operation = operation
    def apply(self) -> None:
        self._operation()


class ExpectedStateInitializationService:
    """Atomic EXPECTED_STATE_INITIALIZED revision-1 authority transition。

    只消費已取得的 immutable broker evidence/currentness/authorization；
    不執行 broker I/O，不建立 READY，不補造 Order/Fill history。
    """

    def __init__(
        self,
        *,
        authority_service: AccountAuthorityCommitService,
        initialization_repositories: Callable[
            [UnitOfWork],
            tuple[EventLedgerRepository, ExpectedPositionSnapshotRepository, BrokerPositionObservationRepository],
        ],
    ) -> None:
        self._authority_service = authority_service
        self._initialization_repositories = initialization_repositories

    def initialize(
        self,
        request: ExpectedStateInitializationRequest,
        *,
        authorization_provider: ProtectedActionAuthorizationProvider | None,
        currentness_provider: InitializationCurrentnessProvider | None,
    ) -> AccountAuthorityCommitReceipt:
        resource = f"{request.observation.broker}:{request.observation.account_ref}"
        authorization: ProtectedActionAuthorization = require_protected_action_authorization(
            provider=authorization_provider,
            authorization_id=request.authorization_id,
            environment=request.environment,
            action="EXPECTED_STATE_INITIALIZE",
            resource=resource,
            protected_world_fingerprint=request.protected_world_fingerprint,
            command_id=request.command_id,
            correlation_id=request.correlation_id,
        )
        if currentness_provider is None or currentness_provider.environment is not request.environment:
            raise ExpectedStateInitializationError("broker currentness authority is unavailable")
        currentness = currentness_provider.verify(request.protected_world_fingerprint)
        if (
            currentness is None
            or currentness.environment is not request.environment
            or currentness.protected_world_fingerprint != request.protected_world_fingerprint
        ):
            raise ExpectedStateInitializationError("broker currentness evidence is invalid")

        event = TradingEvent(
            event_id=request.event_id,
            event_type="EXPECTED_STATE_INITIALIZED",
            source="ACCOUNT_AUTHORITY",
            entity_type="BROKER_ACCOUNT",
            entity_id=resource,
            occurred_at=request.confirmed_at,
            received_at=request.confirmed_at,
            sequence=1,
            event_version=1,
            idempotency_scope=f"EXPECTED_STATE_INITIALIZED:{resource}",
            idempotency_key=request.authority_commit_id,
            correlation_id=request.correlation_id,
            causation_id=request.command_id,
            payload_json={
                "mode": request.mode.value,
                "broker_observation_id": request.observation.observation_id,
                "seeded_positions": [p.model_dump(mode="json") for p in request.seeded_positions],
                "confirmed_by": request.confirmed_by,
                "confirmed_at": request.confirmed_at.isoformat(),
                "reason": request.reason,
                "authorization_id": authorization.authorization_id,
                "currentness_evidence_id": currentness.evidence_id,
            },
        )
        snapshot = AccountPositionSnapshot(
            snapshot_id=request.snapshot_id,
            broker=request.observation.broker,
            account_ref=request.observation.account_ref,
            effective_at=request.confirmed_at,
            recorded_at=request.confirmed_at,
            source_event_id=request.event_id,
            positions=request.seeded_positions,
        )

        def participants(uow: UnitOfWork) -> tuple[AccountAuthorityParticipant, ...]:
            event_repo, snapshot_repo, observation_repo = self._initialization_repositories(uow)

            def append_event() -> None:
                result = event_repo.append(event)
                if result.status is not EventAppendStatus.APPENDED:
                    raise AccountAuthorityIntegrityError(
                        "initialization event exists without matching authority receipt"
                    )

            return (
                _Apply(lambda: observation_repo.append(request.observation)),
                _Apply(append_event),
                _Apply(lambda: snapshot_repo.append(snapshot)),
            )

        return self._authority_service.commit(
            AccountAuthorityCommit(
                authority_commit_id=request.authority_commit_id,
                mutation_fingerprint=request.mutation_fingerprint,
                broker=request.observation.broker,
                account_ref=request.observation.account_ref,
                expected_head_revision=0,
                expected_snapshot_id=request.snapshot_id,
                recorded_at=request.confirmed_at,
            ),
            participant_factory=participants,
            initialization=True,
        )


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
