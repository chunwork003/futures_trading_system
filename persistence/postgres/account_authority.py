from __future__ import annotations

import json
from typing import Any

from persistence.account_authority import (
    AccountAuthorityCommitReceipt,
    AccountAuthorityConflictError,
    AccountRecoveryCheckpoint,
    AccountStateHead,
)


class PostgresAccountAuthorityRepository:
    """PostgreSQL account authority adapter；只參與 caller-owned transaction，不自行 commit。"""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def lock_head(self, broker: str, account_ref: str) -> AccountStateHead | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT broker, account_ref, current_revision, initialized "
                "FROM trading.account_state_heads "
                "WHERE broker=%s AND account_ref=%s FOR UPDATE",
                (broker.upper(), account_ref),
            )
            row = cursor.fetchone()
        return None if row is None else AccountStateHead(
            broker=row[0], account_ref=row[1], current_revision=row[2], initialized=row[3]
        )

    def lock_or_create_reserved_head(
        self,
        broker: str,
        account_ref: str,
    ) -> AccountStateHead:
        """在 caller-owned transaction 中 concurrency-safe bootstrap rev0，並鎖定 exact head。"""

        normalized_broker = broker.upper()
        with self._connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO trading.account_state_heads "
                "(broker, account_ref, current_revision, initialized) "
                "VALUES (%s,%s,0,FALSE) ON CONFLICT (broker, account_ref) DO NOTHING",
                (normalized_broker, account_ref),
            )
            cursor.execute(
                "SELECT broker, account_ref, current_revision, initialized "
                "FROM trading.account_state_heads "
                "WHERE broker=%s AND account_ref=%s FOR UPDATE",
                (normalized_broker, account_ref),
            )
            row = cursor.fetchone()
        if row is None:
            raise AccountAuthorityConflictError(
                "reserved account authority head bootstrap did not resolve"
            )
        return AccountStateHead(
            broker=row[0],
            account_ref=row[1],
            current_revision=row[2],
            initialized=row[3],
        )

    def get_head(self, broker: str, account_ref: str) -> AccountStateHead | None:
        """讀取 durable head 以驗證 historical receipt closure；不鎖定、不推進 revision。"""

        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT broker, account_ref, current_revision, initialized "
                "FROM trading.account_state_heads "
                "WHERE broker=%s AND account_ref=%s",
                (broker.upper(), account_ref),
            )
            row = cursor.fetchone()
        return None if row is None else AccountStateHead(
            broker=row[0],
            account_ref=row[1],
            current_revision=row[2],
            initialized=row[3],
        )

    def advance_head(self, head: AccountStateHead, *, expected_revision: int) -> None:
        if head.current_revision != expected_revision + 1:
            raise AccountAuthorityConflictError("account revision must advance contiguously")
        with self._connection.cursor() as cursor:
            cursor.execute(
                "UPDATE trading.account_state_heads SET current_revision=%s, initialized=%s "
                "WHERE broker=%s AND account_ref=%s AND current_revision=%s "
                "RETURNING current_revision",
                (head.current_revision, head.initialized, head.broker, head.account_ref, expected_revision),
            )
            if cursor.fetchone() is None:
                raise AccountAuthorityConflictError("account revision head conflict")

    def append_checkpoint(self, checkpoint: AccountRecoveryCheckpoint) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO trading.account_recovery_checkpoints "
                "(broker, account_ref, account_revision, expected_snapshot_id, authority_commit_id, recorded_at, checkpoint_json) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING account_revision",
                (*checkpoint.model_dump(mode="json").values(), json.dumps(checkpoint.model_dump(mode="json"))),
            )
            if cursor.fetchone() is None:
                raise AccountAuthorityConflictError("account recovery checkpoint conflict")

    def get_checkpoint(self, broker: str, account_ref: str, account_revision: int) -> AccountRecoveryCheckpoint | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT checkpoint_json FROM trading.account_recovery_checkpoints "
                "WHERE broker=%s AND account_ref=%s AND account_revision=%s",
                (broker.upper(), account_ref, account_revision),
            )
            row = cursor.fetchone()
        return None if row is None else AccountRecoveryCheckpoint.model_validate(row[0])

    def append_receipt(self, receipt: AccountAuthorityCommitReceipt) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO trading.account_authority_commit_receipts "
                "(authority_commit_id, mutation_fingerprint, broker, account_ref, committed_revision, expected_snapshot_id, recorded_at, receipt_json) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING RETURNING authority_commit_id",
                (*receipt.model_dump(mode="json").values(), json.dumps(receipt.model_dump(mode="json"))),
            )
            if cursor.fetchone() is None:
                raise AccountAuthorityConflictError("account authority receipt conflict")

    def get_receipt(self, authority_commit_id: str) -> AccountAuthorityCommitReceipt | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                "SELECT receipt_json FROM trading.account_authority_commit_receipts WHERE authority_commit_id=%s",
                (authority_commit_id,),
            )
            row = cursor.fetchone()
        return None if row is None else AccountAuthorityCommitReceipt.model_validate(row[0])
