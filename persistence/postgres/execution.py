from __future__ import annotations

import json
from typing import Any

from persistence.execution import OrderProjectionConflictError
from trading.execution import Fill, Order


class PostgresOrderRepository:
    """Derived order projection adapter；保留 immutable client ref 與 optimistic version。"""

    def __init__(self, connection: Any) -> None: self._connection = connection

    def get(self, order_id: str) -> Order | None:
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT projection_json FROM trading.orders WHERE order_id = %s", (order_id,))
            row = cursor.fetchone()
        return None if row is None else Order.model_validate(row[0])

    def save(self, order: Order, *, expected_version: int) -> None:
        payload = json.loads(order.model_dump_json())
        with self._connection.cursor() as cursor:
            if expected_version == -1:
                if order.version != 0 or order.broker_client_order_ref is None:
                    raise OrderProjectionConflictError(
                        "initial durable order requires sequence-0 broker client ref"
                    )
                cursor.execute(
                    "INSERT INTO trading.orders (order_id, intent_id, correlation_id, broker_client_order_ref, broker_order_id, instrument_id, contract_id, status, version, projection_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING order_id",
                    (order.order_id, order.intent_id, order.correlation_id, order.broker_client_order_ref, order.broker_order_id, order.instrument_id, order.contract_id, order.status.value, order.version, json.dumps(payload)),
                )
            else:
                if order.broker_client_order_ref is None:
                    raise OrderProjectionConflictError(
                        "durable order projection requires broker client ref"
                    )
                cursor.execute(
                    "UPDATE trading.orders SET broker_order_id=%s, status=%s, version=%s, projection_json=%s WHERE order_id=%s AND version=%s AND broker_client_order_ref=%s RETURNING order_id",
                    (order.broker_order_id, order.status.value, order.version, json.dumps(payload), order.order_id, expected_version, order.broker_client_order_ref),
                )
            if cursor.fetchone() is None:
                raise OrderProjectionConflictError(order.order_id)


class PostgresFillRepository:
    """Immutable Fill evidence adapter；相同 fill 可 dedup，不同內容明確 conflict。"""

    def __init__(self, connection: Any) -> None: self._connection = connection

    def get(self, fill_id: str) -> Fill | None:
        with self._connection.cursor() as cursor:
            cursor.execute("SELECT fill_json FROM trading.fills WHERE fill_id = %s", (fill_id,))
            row = cursor.fetchone()
        return None if row is None else Fill.model_validate(row[0])

    def append(self, fill: Fill) -> bool:
        existing = self.get(fill.fill_id)
        if existing is not None: return existing == fill
        payload = json.loads(fill.model_dump_json())
        with self._connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO trading.fills (fill_id, order_id, event_id, quantity, price, occurred_at, broker_deal_id, fill_json) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING fill_id",
                (fill.fill_id, fill.order_id, fill.event_id, fill.quantity, fill.price, fill.occurred_at, fill.broker_deal_id, json.dumps(payload)),
            )
            inserted = cursor.fetchone() is not None
        return inserted or self.get(fill.fill_id) == fill
