from __future__ import annotations

import json
from typing import Any

from persistence.broker_action import (
    BrokerActionAttempt,
    BrokerActionConflictError,
    BrokerActionHead,
    BrokerActionKind,
    BrokerActionResolution,
)


class PostgresBrokerActionRepository:
    """PostgreSQL durable broker-action adapter；DB conditional writes 防止並行 unresolved attempt。

    Connection/UoW 由上層提供；本 repository 絕不 commit、rollback 或呼叫 broker。
    """

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def get_attempt(self, attempt_id: str) -> BrokerActionAttempt | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT attempt_json FROM trading.broker_action_attempts WHERE attempt_id=%s",
                (attempt_id,),
            )
            row = cursor.fetchone()
        return None if row is None else BrokerActionAttempt.model_validate(row[0])

    def append_attempt(self, attempt: BrokerActionAttempt) -> None:
        payload = json.loads(attempt.model_dump_json())
        with self._connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO trading.broker_action_attempts "
                "(attempt_id, broker, account_ref, order_id, action, broker_client_order_ref, "
                "command_id, correlation_id, authorization_id, created_at, attempt_json) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT DO NOTHING RETURNING attempt_id",
                (
                    attempt.attempt_id, attempt.broker, attempt.account_ref,
                    attempt.order_id, attempt.action.value,
                    attempt.broker_client_order_ref, attempt.command_id,
                    attempt.correlation_id, attempt.authorization_id,
                    attempt.created_at, json.dumps(payload),
                ),
            )
            inserted = cursor.fetchone()
        if inserted is None:
            existing = self.get_attempt(attempt.attempt_id)
            if existing != attempt:
                raise BrokerActionConflictError("broker action attempt identity conflict")

    def get_head(
        self, broker: str, account_ref: str, order_id: str, action: BrokerActionKind
    ) -> BrokerActionHead | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT broker, account_ref, order_id, action, version, unresolved_attempt_id "
                "FROM trading.broker_action_heads "
                "WHERE broker=%s AND account_ref=%s AND order_id=%s AND action=%s",
                (broker, account_ref, order_id, action.value),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        return BrokerActionHead(
            broker=row[0], account_ref=row[1], order_id=row[2], action=row[3],
            version=row[4], unresolved_attempt_id=row[5],
        )

    def reserve_head(self, attempt: BrokerActionAttempt, *, expected_version: int) -> None:
        with self._connection.cursor() as cursor:
            if expected_version == -1:
                cursor.execute(
                    "INSERT INTO trading.broker_action_heads "
                    "(broker, account_ref, order_id, action, version, unresolved_attempt_id) "
                    "VALUES (%s,%s,%s,%s,1,%s) ON CONFLICT DO NOTHING RETURNING version",
                    (
                        attempt.broker, attempt.account_ref, attempt.order_id,
                        attempt.action.value, attempt.attempt_id,
                    ),
                )
            else:
                cursor.execute(
                    "UPDATE trading.broker_action_heads "
                    "SET version=version+1, unresolved_attempt_id=%s "
                    "WHERE broker=%s AND account_ref=%s AND order_id=%s AND action=%s "
                    "AND version=%s AND unresolved_attempt_id IS NULL RETURNING version",
                    (
                        attempt.attempt_id, attempt.broker, attempt.account_ref,
                        attempt.order_id, attempt.action.value, expected_version,
                    ),
                )
            if cursor.fetchone() is None:
                raise BrokerActionConflictError(
                    "concurrent or unresolved broker action blocks reservation"
                )

    def append_resolution(self, resolution: BrokerActionResolution) -> None:
        payload = json.loads(resolution.model_dump_json())
        with self._connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO trading.broker_action_resolutions "
                "(resolution_id, attempt_id, kind, resolved_at, resolution_json) "
                "VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING resolution_id",
                (
                    resolution.resolution_id, resolution.attempt_id,
                    resolution.kind.value, resolution.resolved_at, json.dumps(payload),
                ),
            )
            if cursor.fetchone() is None:
                raise BrokerActionConflictError("broker action resolution identity conflict")

    def release_head(self, attempt: BrokerActionAttempt, *, expected_version: int) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "UPDATE trading.broker_action_heads "
                "SET version=version+1, unresolved_attempt_id=NULL "
                "WHERE broker=%s AND account_ref=%s AND order_id=%s AND action=%s "
                "AND version=%s AND unresolved_attempt_id=%s RETURNING version",
                (
                    attempt.broker, attempt.account_ref, attempt.order_id,
                    attempt.action.value, expected_version, attempt.attempt_id,
                ),
            )
            if cursor.fetchone() is None:
                raise BrokerActionConflictError("broker action head release conflict")


__all__ = ["PostgresBrokerActionRepository"]
