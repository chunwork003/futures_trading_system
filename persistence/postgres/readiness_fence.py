from __future__ import annotations

from typing import Any

from persistence.readiness_fence import (
    RecoveryReadinessFenceConflictError,
    RecoveryReadinessFenceToken,
)
from trading.account import BrokerAccount


class PostgresRecoveryReadinessFenceRepository:
    """以 account_recovery_controls row lock 序列化 readiness invalidation；不自行 commit。"""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def lock_active(self, account: BrokerAccount) -> RecoveryReadinessFenceToken | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT broker, account_ref, generation, recovery_cut_revision, "
                "readiness_revision, active FROM trading.account_recovery_controls "
                "WHERE broker=%s AND account_ref=%s FOR UPDATE",
                (account.broker, account.account_ref),
            )
            row = cursor.fetchone()
        if row is None or not row[5]:
            return None
        if (row[0], row[1]) != (account.broker, account.account_ref):
            raise RecoveryReadinessFenceConflictError("recovery readiness fence account mismatch")
        return RecoveryReadinessFenceToken(
            account=account,
            recovery_generation=row[2],
            recovery_cut_revision=row[3],
            captured_readiness_revision=row[4],
        )

    def advance_locked(self, token: RecoveryReadinessFenceToken) -> RecoveryReadinessFenceToken:
        next_revision = token.captured_readiness_revision + 1
        with self._connection.cursor() as cursor:
            cursor.execute(
                "UPDATE trading.account_recovery_controls "
                "SET readiness_revision=readiness_revision+1 "
                "WHERE broker=%s AND account_ref=%s AND generation=%s "
                "AND recovery_cut_revision=%s AND readiness_revision=%s AND active=TRUE "
                "RETURNING readiness_revision",
                (
                    token.account.broker,
                    token.account.account_ref,
                    token.recovery_generation,
                    token.recovery_cut_revision,
                    token.captured_readiness_revision,
                ),
            )
            row = cursor.fetchone()
        if row is None or row[0] != next_revision:
            raise RecoveryReadinessFenceConflictError("recovery readiness fence CAS conflict")
        return token.model_copy(update={"captured_readiness_revision": next_revision})
