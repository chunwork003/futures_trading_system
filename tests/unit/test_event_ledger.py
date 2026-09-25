from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from persistence.contracts import (
    EventIdentityConflictError,
    EventSequenceConflictError,
    IdempotencyConflictError,
)
from persistence.events import (
    EventAppendStatus,
    EventLedgerRepository,
    TradingEvent,
)
from persistence.postgres.event_ledger import PostgresEventLedgerRepository


def make_event(**updates) -> TradingEvent:
    values = {
        "event_id": " EVT-1 ", "event_type": " ORDER_ACCEPTED ", "source": " ENGINE ",
        "entity_type": " ORDER ", "entity_id": " ORD-1 ",
        "occurred_at": datetime(2026, 9, 25, 9, 0, tzinfo=timezone(timedelta(hours=8))),
        "received_at": datetime(2026, 9, 25, 1, 0, 1, tzinfo=timezone.utc),
        "sequence": 1, "event_version": 1,
        "idempotency_scope": " ORDER ", "idempotency_key": " ACCEPT-1 ",
        "correlation_id": " CORR-1 ", "causation_id": None,
        "payload_json": {"z": 2, "a": {"b": 1}},
    }
    values.update(updates)
    return TradingEvent(**values)


class MemoryCursor:
    def __init__(self, connection): self.connection, self.rows, self.row = connection, [], None
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def execute(self, sql, params=None):
        self.connection.executed.append((sql, params))
        rows = self.connection.rows
        if sql.startswith("INSERT"):
            candidate = tuple(params)
            conflict = any(
                row[0] == candidate[0]
                or row[9:11] == candidate[9:11]
                or (row[2], row[3], row[4], row[7])
                == (candidate[2], candidate[3], candidate[4], candidate[7])
                for row in rows
            )
            if conflict:
                self.row = None
            else:
                rows.append(candidate)
                self.row = (candidate[0],)
            return
        if "WHERE event_id" in sql:
            self.row = next((r for r in rows if r[0] == params[0]), None)
        elif "WHERE idempotency_scope" in sql:
            self.row = next((r for r in rows if r[9:11] == params), None)
        elif "AND sequence =" in sql:
            self.row = next((r for r in rows if (r[2], r[3], r[4], r[7]) == params), None)
        elif "sequence >" in sql:
            matching = [r for r in rows if (r[2], r[3], r[4]) == params[:3] and r[7] > params[3]]
            self.rows = sorted(matching, key=lambda r: r[7])[:params[4]]
    def fetchone(self): return self.row
    def fetchall(self): return self.rows


class MemoryConnection:
    autocommit = False
    def __init__(self): self.rows, self.executed, self.commits, self.rollbacks = [], [], 0, 0
    def cursor(self): return MemoryCursor(self)
    def commit(self): self.commits += 1
    def rollback(self): self.rollbacks += 1


def test_trading_event_is_immutable_extra_forbid_normalized_and_canonical() -> None:
    event = make_event()
    assert event.event_id == "EVT-1"
    assert event.occurred_at == datetime(2026, 9, 25, 1, 0, tzinfo=timezone.utc)
    assert event.payload_json == {"a": {"b": 1}, "z": 2}
    with pytest.raises(ValidationError): event.sequence = 2
    with pytest.raises(ValidationError): TradingEvent(**event.model_dump(), extra_field=True)


@pytest.mark.parametrize("updates", [{"sequence": -1}, {"event_version": 0}, {"event_id": " "}, {"occurred_at": datetime(2026, 1, 1)}, {"payload_json": []}, {"payload_json": {"x": float("nan")}}])
def test_trading_event_rejects_invalid_contract_values(updates) -> None:
    with pytest.raises((ValidationError, ValueError)):
        make_event(**updates)


def test_event_ledger_protocol_and_append_duplicate_queries() -> None:
    connection = MemoryConnection(); repository = PostgresEventLedgerRepository(connection); event = make_event()
    assert isinstance(repository, EventLedgerRepository)
    first = repository.append(event); second = repository.append(event)
    assert first.status is EventAppendStatus.APPENDED
    assert second.status is EventAppendStatus.DUPLICATE
    assert repository.get("EVT-1") == event
    assert repository.get_by_idempotency("ORDER", "ACCEPT-1") == event
    assert connection.commits == connection.rollbacks == 0


def test_event_identity_conflict_is_explicit() -> None:
    repository = PostgresEventLedgerRepository(MemoryConnection()); repository.append(make_event())
    with pytest.raises(EventIdentityConflictError):
        repository.append(make_event(payload_json={"changed": True}))


def test_idempotency_conflict_is_explicit() -> None:
    repository = PostgresEventLedgerRepository(MemoryConnection()); repository.append(make_event())
    with pytest.raises(IdempotencyConflictError):
        repository.append(make_event(event_id="EVT-2", sequence=2, payload_json={"changed": True}))


def test_sequence_conflict_is_explicit() -> None:
    repository = PostgresEventLedgerRepository(MemoryConnection()); repository.append(make_event())
    with pytest.raises(EventSequenceConflictError):
        repository.append(make_event(event_id="EVT-2", idempotency_key="ACCEPT-2", payload_json={"changed": True}))


def test_list_after_orders_by_sequence_and_requires_positive_limit() -> None:
    connection = MemoryConnection(); repository = PostgresEventLedgerRepository(connection)
    for sequence in (3, 1, 2):
        repository.append(make_event(event_id=f"EVT-{sequence}", sequence=sequence, idempotency_key=f"KEY-{sequence}"))
    assert [item.sequence for item in repository.list_after("ENGINE", "ORDER", "ORD-1", 1, 2)] == [2, 3]
    with pytest.raises(ValueError, match="positive"):
        repository.list_after("ENGINE", "ORDER", "ORD-1", 0, 0)


def test_received_at_may_precede_occurred_at_and_repository_never_commits() -> None:
    event = make_event(received_at=datetime(2026, 9, 25, 0, 59, tzinfo=timezone.utc))
    connection = MemoryConnection(); PostgresEventLedgerRepository(connection).append(event)
    assert connection.commits == connection.rollbacks == 0
