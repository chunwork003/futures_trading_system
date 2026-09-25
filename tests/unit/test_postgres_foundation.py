from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from persistence.contracts import PersistenceTransactionError
from persistence.postgres.compatibility import (
    POSTGRES_COMPATIBILITY_TARGETS,
    PostgresCompatibilityEvidence,
    PostgresIntegrationStatus,
    detect_postgres_major,
)
from persistence.postgres.driver import connect_postgres
from persistence.postgres.migrations import (
    Migration,
    MigrationConflictError,
    discover_migrations,
    pending_migrations,
    run_migrations,
)
from persistence.postgres.uow import PostgresUnitOfWork


class FakeConnection:
    def __init__(self, *, autocommit: bool = False) -> None:
        self.autocommit = autocommit
        self.commits = 0
        self.rollbacks = 0
        self.closed = 0
        self.executed: list[tuple[str, object]] = []
        self.applied: list[tuple[int, str]] = []

    def commit(self): self.commits += 1
    def rollback(self): self.rollbacks += 1
    def close(self): self.closed += 1
    def cursor(self): return FakeCursor(self)


class FakeCursor:
    def __init__(self, connection: FakeConnection) -> None: self.connection = connection
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def execute(self, sql, params=None):
        self.connection.executed.append((sql, params))
        if sql.startswith("INSERT INTO trading.schema_migrations"):
            self.connection.applied.append(params)
    def fetchall(self): return list(self.connection.applied)


def test_uow_explicit_commit_and_no_double_finalize() -> None:
    connection = FakeConnection()
    with PostgresUnitOfWork(lambda: connection) as uow:
        assert uow.connection is connection
        uow.commit()
        with pytest.raises(PersistenceTransactionError, match="finalized"):
            uow.rollback()
    assert (connection.commits, connection.rollbacks, connection.closed) == (1, 0, 1)


def test_uow_rolls_back_uncommitted_exit_and_exception() -> None:
    uncommitted = FakeConnection()
    with PostgresUnitOfWork(lambda: uncommitted):
        pass
    assert uncommitted.rollbacks == 1
    broken = FakeConnection()
    with pytest.raises(LookupError):
        with PostgresUnitOfWork(lambda: broken):
            raise LookupError("boom")
    assert broken.rollbacks == 1


def test_uow_rejects_autocommit_connection() -> None:
    connection = FakeConnection(autocommit=True)
    with pytest.raises(PersistenceTransactionError, match="autocommit=False"):
        with PostgresUnitOfWork(lambda: connection):
            pass
    assert connection.closed == 1


def test_driver_rejects_blank_dsn_and_requests_autocommit_false(monkeypatch) -> None:
    with pytest.raises(ValueError, match="must not be blank"):
        connect_postgres("  ")
    observed = {}
    fake = SimpleNamespace(connect=lambda dsn, **kwargs: observed.update(dsn=dsn, **kwargs) or object())
    monkeypatch.setitem(__import__("sys").modules, "psycopg", fake)
    connect_postgres(" postgresql://example ")
    assert observed == {"dsn": "postgresql://example", "autocommit": False}


def test_migration_discovery_is_deterministic_and_rejects_duplicate(tmp_path: Path) -> None:
    (tmp_path / "0002_second.sql").write_text("SELECT 2", encoding="utf-8")
    (tmp_path / "0001_first.sql").write_text("SELECT 1", encoding="utf-8")
    assert [item.version for item in discover_migrations(tmp_path)] == [1, 2]
    (tmp_path / "0001_duplicate.sql").write_text("SELECT 3", encoding="utf-8")
    with pytest.raises(MigrationConflictError, match="duplicate"):
        discover_migrations(tmp_path)


def test_applied_migration_name_conflict_is_explicit() -> None:
    migrations = (Migration(1, "event_ledger", "SELECT 1"),)
    with pytest.raises(MigrationConflictError, match="name conflicts"):
        pending_migrations(migrations, ((1, "different"),))


def test_migration_runner_executes_in_order_and_never_commits() -> None:
    connection = FakeConnection()
    run_migrations(connection, (Migration(1, "first", "SELECT 1"), Migration(2, "second", "SELECT 2")))
    assert connection.commits == 0
    assert connection.rollbacks == 0
    assert connection.applied == [(1, "first"), (2, "second")]
    sql = [item[0] for item in connection.executed]
    assert sql.index("SELECT 1") < sql.index("SELECT 2")


def test_compatibility_targets_are_exactly_pending_17_and_18() -> None:
    assert [(item.major, item.status) for item in POSTGRES_COMPATIBILITY_TARGETS] == [
        (17, PostgresIntegrationStatus.PENDING),
        (18, PostgresIntegrationStatus.PENDING),
    ]
    assert all(item.server_version_num is None for item in POSTGRES_COMPATIBILITY_TARGETS)


def test_compatibility_evidence_requires_explicit_metadata() -> None:
    with pytest.raises(ValidationError, match="cannot claim"):
        PostgresCompatibilityEvidence(
            major=17, status=PostgresIntegrationStatus.PENDING, verified_on=date(2026, 9, 25)
        )
    with pytest.raises(ValidationError, match="requires explicit"):
        PostgresCompatibilityEvidence(major=17, status=PostgresIntegrationStatus.VERIFIED)
    verified = PostgresCompatibilityEvidence(
        major=17, status=PostgresIntegrationStatus.VERIFIED,
        server_version_num=170006, driver_version="3.3.6",
        verified_on=date(2026, 9, 25), evidence=("migration and rollback smoke passed",),
    )
    assert verified.status is PostgresIntegrationStatus.VERIFIED


def test_detect_postgres_major_is_pure() -> None:
    assert detect_postgres_major(170006) == 17
    assert detect_postgres_major(180001) == 18
    with pytest.raises(ValueError):
        detect_postgres_major(0)


def test_event_ledger_migration_has_operational_constraints_and_chinese_comments() -> None:
    path = Path("persistence/postgres/migrations/0001_event_ledger.sql")
    sql = path.read_text(encoding="utf-8")
    for token in ("PRIMARY KEY", "UNIQUE", "CHECK", "TIMESTAMPTZ", "JSONB", "COMMENT ON"):
        assert token in sql
    assert "交易系統不可變事件帳本" in sql
