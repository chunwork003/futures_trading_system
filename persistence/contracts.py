from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Protocol, runtime_checkable


class PersistenceContractError(ValueError):
    """Canonical persistence value 違反 identity、numeric 或 time contract。"""


class PersistenceTransactionError(RuntimeError):
    """Transaction lifecycle 違反 explicit-finalization contract。"""


class PersistenceConflictError(RuntimeError):
    """Append-only storage 的 canonical identity 或版本發生衝突。"""


class EventIdentityConflictError(PersistenceConflictError):
    """相同 event ID 對應不同 canonical event。"""


class EventSequenceConflictError(PersistenceConflictError):
    """相同 entity sequence scope 對應不同 canonical event。"""


class IdempotencyConflictError(PersistenceConflictError):
    """相同 idempotency scope/key 對應不同 canonical event。"""


def normalize_stable_id(value: str) -> str:
    """正規化 caller-supplied stable ID；backend 不得另行改寫。"""

    if not isinstance(value, str):
        raise PersistenceContractError("stable ID must be a string")
    normalized = value.strip()
    if not normalized:
        raise PersistenceContractError("stable ID must not be blank")
    return normalized


def require_exact_decimal(value: Decimal) -> Decimal:
    """只接受 finite Decimal，避免 persistence/accounting 路徑混入 float。"""

    if not isinstance(value, Decimal):
        raise PersistenceContractError("exact value must be Decimal")
    if not value.is_finite():
        raise PersistenceContractError("exact Decimal must be finite")
    return value


def normalize_aware_utc(value: datetime) -> datetime:
    """拒絕 naive time，並將具時區 timestamp 正規化為 UTC。"""

    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise PersistenceContractError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


@runtime_checkable
class AppendOnlyRepository(Protocol):
    """Append-only repository port；刻意不暴露 update/delete 或 transaction authority。"""

    def append(self, record: Any) -> Any: ...


@runtime_checkable
class SnapshotRepository(Protocol):
    """Snapshot history port；latest/as-of 均為唯讀查詢。"""

    def append_snapshot(self, snapshot: Any) -> None: ...
    def latest(self, key: Any) -> Any | None: ...
    def as_of(self, key: Any, at: datetime) -> Any | None: ...


@runtime_checkable
class UnitOfWork(Protocol):
    """Explicit commit transaction port；離開 context 未 commit 必須 rollback。"""

    def __enter__(self) -> UnitOfWork: ...
    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
