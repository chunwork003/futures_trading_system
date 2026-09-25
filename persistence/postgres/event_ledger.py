from __future__ import annotations

import json
from typing import Any

from persistence.contracts import (
    EventIdentityConflictError,
    EventSequenceConflictError,
    IdempotencyConflictError,
    PersistenceConflictError,
    normalize_stable_id,
)
from persistence.events import EventAppendResult, EventAppendStatus, TradingEvent


_COLUMNS = (
    "event_id, event_type, source, entity_type, entity_id, occurred_at, received_at, "
    "sequence, event_version, idempotency_scope, idempotency_key, correlation_id, "
    "causation_id, payload_json"
)


def _event_params(event: TradingEvent) -> tuple[Any, ...]:
    return (
        event.event_id, event.event_type, event.source, event.entity_type,
        event.entity_id, event.occurred_at, event.received_at, event.sequence,
        event.event_version, event.idempotency_scope, event.idempotency_key,
        event.correlation_id, event.causation_id,
        json.dumps(event.payload_json, sort_keys=True, separators=(",", ":"), ensure_ascii=False),
    )


def _row_to_event(row: tuple[Any, ...] | None) -> TradingEvent | None:
    if row is None:
        return None
    payload = row[13]
    if isinstance(payload, str):
        payload = json.loads(payload)
    return TradingEvent(
        event_id=row[0], event_type=row[1], source=row[2], entity_type=row[3],
        entity_id=row[4], occurred_at=row[5], received_at=row[6], sequence=row[7],
        event_version=row[8], idempotency_scope=row[9], idempotency_key=row[10],
        correlation_id=row[11], causation_id=row[12], payload_json=payload,
    )


class PostgresEventLedgerRepository:
    """PostgreSQL append-only ledger；transaction finalize 完全由 UnitOfWork 負責。"""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def append(self, event: TradingEvent) -> EventAppendResult:
        existing_id = self.get(event.event_id)
        if existing_id is not None:
            if existing_id == event:
                return EventAppendResult(status=EventAppendStatus.DUPLICATE, event_id=event.event_id)
            raise EventIdentityConflictError(event.event_id)
        existing_key = self.get_by_idempotency(event.idempotency_scope, event.idempotency_key)
        if existing_key is not None:
            if existing_key == event:
                return EventAppendResult(status=EventAppendStatus.DUPLICATE, event_id=event.event_id)
            raise IdempotencyConflictError(event.idempotency_key)
        existing_sequence = self._get_by_sequence(event)
        if existing_sequence is not None:
            if existing_sequence == event:
                return EventAppendResult(status=EventAppendStatus.DUPLICATE, event_id=event.event_id)
            raise EventSequenceConflictError(str(event.sequence))
        with self._connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO trading.event_ledger ({_COLUMNS}) VALUES ("
                + ", ".join(["%s"] * 14)
                + ") ON CONFLICT DO NOTHING RETURNING event_id",
                _event_params(event),
            )
            if cursor.fetchone() is not None:
                return EventAppendResult(
                    status=EventAppendStatus.APPENDED,
                    event_id=event.event_id,
                )

        # Concurrent insert 可能在 pre-check 後取得 unique key；以未中止的
        # transaction 重新讀取三種 scope，保留精確 conflict semantics。
        existing_id = self.get(event.event_id)
        if existing_id is not None:
            if existing_id == event:
                return EventAppendResult(status=EventAppendStatus.DUPLICATE, event_id=event.event_id)
            raise EventIdentityConflictError(event.event_id)
        existing_key = self.get_by_idempotency(event.idempotency_scope, event.idempotency_key)
        if existing_key is not None:
            if existing_key == event:
                return EventAppendResult(status=EventAppendStatus.DUPLICATE, event_id=event.event_id)
            raise IdempotencyConflictError(event.idempotency_key)
        if self._get_by_sequence(event) is not None:
            raise EventSequenceConflictError(str(event.sequence))
        raise PersistenceConflictError("event append conflict could not be classified")

    def _fetch_one(self, sql: str, params: tuple[Any, ...]) -> TradingEvent | None:
        with self._connection.cursor() as cursor:
            cursor.execute(sql, params)
            return _row_to_event(cursor.fetchone())

    def get(self, event_id: str) -> TradingEvent | None:
        return self._fetch_one(
            f"SELECT {_COLUMNS} FROM trading.event_ledger WHERE event_id = %s",
            (normalize_stable_id(event_id),),
        )

    def get_by_idempotency(self, scope: str, key: str) -> TradingEvent | None:
        return self._fetch_one(
            f"SELECT {_COLUMNS} FROM trading.event_ledger "
            "WHERE idempotency_scope = %s AND idempotency_key = %s",
            (normalize_stable_id(scope), normalize_stable_id(key)),
        )

    def _get_by_sequence(self, event: TradingEvent) -> TradingEvent | None:
        return self._fetch_one(
            f"SELECT {_COLUMNS} FROM trading.event_ledger "
            "WHERE source = %s AND entity_type = %s AND entity_id = %s AND sequence = %s",
            (event.source, event.entity_type, event.entity_id, event.sequence),
        )

    def list_after(
        self, source: str, entity_type: str, entity_id: str,
        after_sequence: int, limit: int,
    ) -> tuple[TradingEvent, ...]:
        if limit <= 0:
            raise ValueError("limit must be positive")
        with self._connection.cursor() as cursor:
            cursor.execute(
                f"SELECT {_COLUMNS} FROM trading.event_ledger "
                "WHERE source = %s AND entity_type = %s AND entity_id = %s "
                "AND sequence > %s ORDER BY sequence ASC LIMIT %s",
                (
                    normalize_stable_id(source), normalize_stable_id(entity_type),
                    normalize_stable_id(entity_id), after_sequence, limit,
                ),
            )
            return tuple(_row_to_event(row) for row in cursor.fetchall())  # type: ignore[misc]
