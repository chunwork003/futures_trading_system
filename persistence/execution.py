from __future__ import annotations

from typing import Callable, Protocol, runtime_checkable

from persistence.account import AccountPositionSnapshot, ExpectedPositionSnapshotRepository
from persistence.account_authority import (
    AccountAuthorityCommit,
    AccountAuthorityCommitReceipt,
    AccountAuthorityCommitService,
)
from persistence.contracts import PersistenceConflictError, UnitOfWork
from persistence.events import EventAppendStatus, EventLedgerRepository, TradingEvent
from persistence.contracts import PersistenceContractError
from trading.execution import Fill, Order, OrderEvent, validate_order_event_transition
from persistence.strategy_state import StrategyStateRepository, StrategyStateSnapshot


class OrderProjectionConflictError(PersistenceConflictError):
    """Order derived projection optimistic version 不一致。"""


class DuplicateOrderEventWithoutAuthorityReceiptError(PersistenceContractError):
    """事件已存在但缺少相符 authority receipt，禁止視為成功的新提交。"""


@runtime_checkable
class OrderRepository(Protocol):
    def get(self, order_id: str) -> Order | None: ...
    def save(self, order: Order, *, expected_version: int) -> None: ...


@runtime_checkable
class FillRepository(Protocol):
    def append(self, fill: Fill) -> bool: ...
    def get(self, fill_id: str) -> Fill | None: ...


def order_event_as_trading_event(event: OrderEvent) -> TradingEvent:
    """將 canonical OrderEvent 映射至既有 ledger envelope，避免第二套 event history。"""

    return TradingEvent(
        event_id=event.event_id, event_type="ORDER_STATUS_CHANGED", source="OMS",
        entity_type="ORDER", entity_id=event.order_id, occurred_at=event.occurred_at,
        received_at=event.received_at, sequence=event.sequence, event_version=1,
        idempotency_scope=f"ORDER_EVENT:{event.order_id}",
        idempotency_key=event.idempotency_key, correlation_id=event.correlation_id,
        causation_id=event.causation_id,
        payload_json={
            "previous_status": None if event.previous_status is None else event.previous_status.value,
            "status": event.status.value, "broker_order_id": event.broker_order_id,
            "payload": event.payload_json,
        },
    )


class ExecutionPersistenceParticipant:
    """AccountAuthorityCommit 內的 execution material participant；不自行 commit。"""

    def __init__(
        self,
        *,
        event_repo: EventLedgerRepository,
        fill_repo: FillRepository,
        order_repo: OrderRepository,
        snapshot_repo: ExpectedPositionSnapshotRepository,
        event: OrderEvent,
        previous_event: OrderEvent | None,
        fills: tuple[Fill, ...],
        order: Order,
        expected_version: int,
        expected_snapshot: AccountPositionSnapshot | None,
    ) -> None:
        self._repositories = (event_repo, fill_repo, order_repo, snapshot_repo)
        self._event = event
        self._previous_event = previous_event
        self._fills = fills
        self._order = order
        self._expected_version = expected_version
        self._expected_snapshot = expected_snapshot
        self.status: EventAppendStatus | None = None

    def apply(self) -> None:
        event_repo, fill_repo, order_repo, snapshot_repo = self._repositories
        append = event_repo.append(order_event_as_trading_event(self._event))
        if append.status is EventAppendStatus.DUPLICATE:
            raise DuplicateOrderEventWithoutAuthorityReceiptError(
                "duplicate OrderEvent without matching authority receipt"
            )
        validate_order_event_transition(self._previous_event, self._event)
        if (
            self._order.order_id != self._event.order_id
            or self._order.correlation_id != self._event.correlation_id
            or self._order.status is not self._event.status
            or self._order.version != self._event.sequence
        ):
            raise PersistenceContractError("order projection does not match OrderEvent")
        if self._event.sequence == 0 and self._order.broker_client_order_ref is None:
            raise PersistenceContractError(
                "durable sequence-0 PENDING requires broker_client_order_ref"
            )
        expected_causation = (
            self._order.intent_id
            if self._previous_event is None
            else self._previous_event.event_id
        )
        if self._event.causation_id != expected_causation:
            raise PersistenceContractError("OrderEvent causation chain is invalid")
        for fill in self._fills:
            if (
                fill.order_id != self._event.order_id
                or fill.event_id != self._event.event_id
                or fill.correlation_id != self._event.correlation_id
                or fill.causation_id != self._event.event_id
            ):
                raise PersistenceContractError(
                    "Fill provenance does not match producing OrderEvent"
                )
            if not fill_repo.append(fill):
                raise PersistenceConflictError(f"fill conflict: {fill.fill_id}")
        order_repo.save(self._order, expected_version=self._expected_version)
        if self._fills and self._expected_snapshot is None:
            raise PersistenceContractError(
                "material Fill update requires a complete expected-position snapshot"
            )
        if self._expected_snapshot is not None:
            if self._expected_snapshot.source_event_id != self._event.event_id:
                raise PersistenceContractError(
                    "expected snapshot source_event_id mismatch"
                )
            snapshot_repo.append(self._expected_snapshot)
        self.status = EventAppendStatus.APPENDED


class ExecutionPersistenceService:
    """保留 legacy caller-owned UoW facade，並可產生不自行 finalize 的 transaction participant。"""

    def __init__(
        self,
        *,
        uow_factory: Callable[[], UnitOfWork],
        repositories: Callable[[UnitOfWork], tuple[EventLedgerRepository, FillRepository, OrderRepository, ExpectedPositionSnapshotRepository]],
    ) -> None:
        self._uow_factory = uow_factory
        self._repositories = repositories

    def apply(
        self,
        *,
        event: OrderEvent,
        previous_event: OrderEvent | None,
        fills: tuple[Fill, ...],
        order: Order,
        expected_version: int,
        expected_snapshot: AccountPositionSnapshot | None = None,
    ) -> EventAppendStatus:
        with self._uow_factory() as uow:
            participant = self.participant(
                uow=uow,
                event=event,
                previous_event=previous_event,
                fills=fills,
                order=order,
                expected_version=expected_version,
                expected_snapshot=expected_snapshot,
            )
            try:
                participant.apply()
            except DuplicateOrderEventWithoutAuthorityReceiptError:
                return EventAppendStatus.DUPLICATE
            uow.commit()
            return EventAppendStatus.APPENDED

    def participant(
        self,
        *,
        uow: UnitOfWork,
        event: OrderEvent,
        previous_event: OrderEvent | None,
        fills: tuple[Fill, ...],
        order: Order,
        expected_version: int,
        expected_snapshot: AccountPositionSnapshot | None = None,
    ) -> ExecutionPersistenceParticipant:
        """建立可參與外層 AccountAuthorityCommit 的無 commit participant。"""

        event_repo, fill_repo, order_repo, snapshot_repo = self._repositories(uow)
        return ExecutionPersistenceParticipant(
            event_repo=event_repo,
            fill_repo=fill_repo,
            order_repo=order_repo,
            snapshot_repo=snapshot_repo,
            event=event,
            previous_event=previous_event,
            fills=fills,
            order=order,
            expected_version=expected_version,
            expected_snapshot=expected_snapshot,
        )


class _StrategySnapshotParticipant:
    def __init__(
        self,
        repository: StrategyStateRepository,
        snapshot: StrategyStateSnapshot,
    ) -> None:
        self._repository = repository
        self._snapshot = snapshot

    def apply(self) -> None:
        self._repository.append(self._snapshot)


class DurablePendingSubmissionService:
    """Atomic 建立 broker-bound sequence-0 PENDING 因果邊界。

    Caller 只傳入已被接受為 material output 的 strategy snapshots；
    HOLD-only evaluation 不會自動被納入。本 service 不執行 broker I/O。
    """

    def __init__(
        self,
        *,
        authority_service: AccountAuthorityCommitService,
        execution_service: ExecutionPersistenceService,
        strategy_repository: Callable[[UnitOfWork], StrategyStateRepository],
    ) -> None:
        self._authority_service = authority_service
        self._execution_service = execution_service
        self._strategy_repository = strategy_repository

    def commit_pending(
        self,
        *,
        mutation: AccountAuthorityCommit,
        event: OrderEvent,
        order: Order,
        material_strategy_snapshots: tuple[StrategyStateSnapshot, ...] = (),
    ) -> AccountAuthorityCommitReceipt:
        if event.sequence != 0 or event.status is not order.status:
            raise PersistenceContractError(
                "durable pending boundary requires matching sequence-0 PENDING"
            )
        if mutation.expected_snapshot_id.strip() == "":
            raise PersistenceContractError("exact expected snapshot reference is required")

        def participants(uow: UnitOfWork):
            execution = self._execution_service.participant(
                uow=uow,
                event=event,
                previous_event=None,
                fills=(),
                order=order,
                expected_version=-1,
            )
            repository = self._strategy_repository(uow)
            return (execution,) + tuple(
                _StrategySnapshotParticipant(repository, snapshot)
                for snapshot in material_strategy_snapshots
            )

        return self._authority_service.commit(
            mutation,
            participant_factory=participants,
        )
