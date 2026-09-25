from __future__ import annotations

from typing import Any, Callable

from persistence.contracts import PersistenceTransactionError


class PostgresUnitOfWork:
    """PostgreSQL transaction authority；repository 不得自行 commit/rollback。"""

    def __init__(self, connection_factory: Callable[[], Any]) -> None:
        self._connection_factory = connection_factory
        self._connection: Any | None = None
        self._finalized = False

    @property
    def connection(self) -> Any:
        if self._connection is None:
            raise PersistenceTransactionError("unit of work is not active")
        return self._connection

    def __enter__(self) -> PostgresUnitOfWork:
        if self._connection is not None:
            raise PersistenceTransactionError("unit of work is already active")
        connection = self._connection_factory()
        if getattr(connection, "autocommit", None) is not False:
            connection.close()
            raise PersistenceTransactionError("PostgreSQL connection requires autocommit=False")
        self._connection = connection
        return self

    def commit(self) -> None:
        self._ensure_open()
        self.connection.commit()
        self._finalized = True

    def rollback(self) -> None:
        self._ensure_open()
        self.connection.rollback()
        self._finalized = True

    def _ensure_open(self) -> None:
        if self._connection is None:
            raise PersistenceTransactionError("unit of work is not active")
        if self._finalized:
            raise PersistenceTransactionError("unit of work is already finalized")

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        if self._connection is None:
            return False
        try:
            if not self._finalized:
                self._connection.rollback()
                self._finalized = True
        finally:
            self._connection.close()
            self._connection = None
        return False
