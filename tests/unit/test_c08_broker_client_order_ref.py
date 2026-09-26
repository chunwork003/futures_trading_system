from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from persistence.execution import ExecutionPersistenceService, OrderProjectionConflictError
from persistence.events import EventAppendResult, EventAppendStatus
from persistence.postgres.execution import PostgresOrderRepository
from trading.account import PositionDirection
from trading.execution import Order, OrderEvent, OrderStatus, OrderType, PositionEffect


NOW = datetime(2026, 9, 27, tzinfo=timezone.utc)


def order(**updates):
    values=dict(order_id="ORDER-1", intent_id="INTENT-1", correlation_id="CORR-1",
                broker_client_order_ref="CLIENT-1", broker_order_id=None, instrument_id=1,
                contract_id=101, direction=PositionDirection.LONG, position_effect=PositionEffect.OPEN,
                order_type=OrderType.MARKET, quantity=1, status=OrderStatus.PENDING,
                version=0, created_at=NOW, updated_at=NOW)
    values.update(updates); return Order(**values)


def event():
    return OrderEvent(event_id="EVENT-0", order_id="ORDER-1", correlation_id="CORR-1",
                      causation_id="INTENT-1", idempotency_key="PENDING-1", sequence=0,
                      previous_status=None, status=OrderStatus.PENDING,
                      occurred_at=NOW, received_at=NOW)


class Uow:
    def __init__(self): self.committed=False; self.rolled=False
    def __enter__(self): return self
    def commit(self): self.committed=True
    def __exit__(self, typ, exc, tb):
        if not self.committed: self.rolled=True
        return False


class Repo:
    def append(self, value):
        if hasattr(value, "event_type"):
            return EventAppendResult(status=EventAppendStatus.APPENDED, event_id=value.event_id)
        return True
    def save(self, value, *, expected_version): pass


def test_order_client_ref_is_normalized_immutable_and_distinct_from_broker_id() -> None:
    item=order(broker_client_order_ref=" CLIENT-1 ", broker_order_id="BROKER-9")
    assert item.broker_client_order_ref == "CLIENT-1"
    assert item.broker_client_order_ref != item.broker_order_id
    with pytest.raises(ValidationError): item.broker_client_order_ref = "OTHER"


def test_transient_order_may_omit_ref_but_durable_pending_rejects_it() -> None:
    item=order(broker_client_order_ref=None)
    uow=Uow(); repo=Repo()
    service=ExecutionPersistenceService(
        uow_factory=lambda:uow, repositories=lambda _: (repo,repo,repo,repo)
    )
    with pytest.raises(ValueError, match="broker_client_order_ref"):
        service.apply(event=event(), previous_event=None, fills=(), order=item, expected_version=-1)
    assert uow.rolled and not uow.committed


class Cursor:
    def __init__(self, connection): self.connection=connection; self.row=None
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def execute(self, sql, params=None):
        self.connection.calls.append((sql,params)); self.row=("ORDER-1",)
    def fetchone(self): return self.row


class Connection:
    def __init__(self): self.calls=[]; self.commits=0
    def cursor(self): return Cursor(self)
    def commit(self): self.commits += 1


def test_postgres_creation_persists_structured_ref_and_never_commits() -> None:
    connection=Connection(); PostgresOrderRepository(connection).save(order(), expected_version=-1)
    sql,params=connection.calls[0]
    assert "broker_client_order_ref" in sql
    assert "CLIENT-1" in params
    assert connection.commits == 0


def test_projection_update_requires_same_durable_ref() -> None:
    connection=Connection()
    PostgresOrderRepository(connection).save(
        order(status=OrderStatus.SUBMITTED, version=1), expected_version=0
    )
    sql,params=connection.calls[0]
    assert "AND broker_client_order_ref=%s" in sql
    assert params[-1] == "CLIENT-1"
    with pytest.raises(OrderProjectionConflictError, match="client ref"):
        PostgresOrderRepository(Connection()).save(
            order(broker_client_order_ref=None, version=1), expected_version=0
        )


def test_ref_has_no_time_window_or_attribute_heuristic_generation() -> None:
    item=order()
    assert item.broker_client_order_ref == "CLIENT-1"
    assert not hasattr(item, "generate_broker_client_order_ref")
    assert not hasattr(PostgresOrderRepository, "match_by_time_window")
