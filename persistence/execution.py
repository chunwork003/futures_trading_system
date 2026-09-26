from __future__ import annotations

from typing import Callable, Protocol, runtime_checkable

from persistence.account import AccountPositionSnapshot, ExpectedPositionSnapshotRepository
from persistence.contracts import PersistenceConflictError, UnitOfWork
from persistence.events import EventAppendStatus, EventLedgerRepository, TradingEvent
from persistence.contracts import PersistenceContractError
from trading.execution import Fill, Order, OrderEvent, validate_order_event_transition


class OrderProjectionConflictError(PersistenceConflictError):
    """Order derived projection optimistic version 不一致。"""


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


class ExecutionPersistenceService:
    """在 caller-owned UoW 原子保存 event/fill/order/expected snapshot。"""

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
            event_repo, fill_repo, order_repo, snapshot_repo = self._repositories(uow)
            append = event_repo.append(order_event_as_trading_event(event))
            if append.status is EventAppendStatus.DUPLICATE:
                return append.status
            validate_order_event_transition(previous_event, event)
            if (
                order.order_id != event.order_id
                or order.correlation_id != event.correlation_id
                or order.status is not event.status
                or order.version != event.sequence
            ):
                raise PersistenceContractError("order projection does not match OrderEvent")
            expected_causation = order.intent_id if previous_event is None else previous_event.event_id
            if event.causation_id != expected_causation:
                raise PersistenceContractError("OrderEvent causation chain is invalid")
            for fill in fills:
                if (
                    fill.order_id != event.order_id
                    or fill.event_id != event.event_id
                    or fill.correlation_id != event.correlation_id
                    or fill.causation_id != event.event_id
                ):
                    raise PersistenceContractError("Fill provenance does not match producing OrderEvent")
                if not fill_repo.append(fill):
                    raise PersistenceConflictError(f"fill conflict: {fill.fill_id}")
            order_repo.save(order, expected_version=expected_version)
            if fills and expected_snapshot is None:
                raise PersistenceContractError(
                    "material Fill update requires a complete expected-position snapshot"
                )
            if expected_snapshot is not None:
                if expected_snapshot.source_event_id != event.event_id:
                    raise PersistenceContractError("expected snapshot source_event_id mismatch")
                snapshot_repo.append(expected_snapshot)
            uow.commit()
            return EventAppendStatus.APPENDED
