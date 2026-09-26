from pathlib import Path

import pytest

from persistence.account import ExpectedStateBaselineNotEstablishedError
from persistence.postgres.account import (
    PostgresExpectedPositionSnapshotRepository,
)
from persistence.broker_action import (
    BrokerActionAttempt,
    BrokerActionKind,
    BrokerActionResolutionKind,
)
from persistence.postgres.broker_action import PostgresBrokerActionRepository
from trading.account import BrokerAccount


def test_operational_migration_has_separate_tables_and_required_types_comments() -> None:
    sql = Path(
        "persistence/postgres/migrations/0002_operational_persistence.sql"
    ).read_text(encoding="utf-8")

    tables = (
        "orders",
        "fills",
        "expected_position_snapshots",
        "expected_position_snapshot_items",
        "broker_position_observations",
        "broker_position_observation_items",
        "account_snapshots",
        "reconciliation_case_history",
        "strategy_instances",
        "strategy_state_snapshots",
    )

    for table in tables:
        assert f"CREATE TABLE trading.{table}" in sql
        assert f"COMMENT ON TABLE trading.{table}" in sql

    for token in (
        "NUMERIC",
        "TIMESTAMPTZ",
        "JSONB",
        "PRIMARY KEY",
        "UNIQUE",
        "CHECK",
    ):
        assert token in sql

    assert "event_ledger" not in "\n".join(
        line
        for line in sql.splitlines()
        if line.startswith("CREATE TABLE")
    )


def test_expected_and_actual_storage_are_structurally_separate() -> None:
    sql = Path(
        "persistence/postgres/migrations/0002_operational_persistence.sql"
    ).read_text(encoding="utf-8")

    assert "trading.expected_position_snapshots" in sql
    assert "trading.broker_position_observations" in sql
    assert "UPDATE trading.reconciliation_case_history" not in sql
    assert "DELETE FROM" not in sql


class _Cursor:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params=None):
        self.connection.last = (sql, params)

    def fetchone(self):
        return None


class _Connection:
    def __init__(self):
        self.last = None
        self.commits = 0

    def cursor(self):
        return _Cursor(self)

    def commit(self):
        self.commits += 1


def test_expected_repository_latest_as_of_order_and_loader_compatibility() -> None:
    connection = _Connection()
    repository = PostgresExpectedPositionSnapshotRepository(connection)

    with pytest.raises(
        ExpectedStateBaselineNotEstablishedError,
        match="baseline is not established",
    ):
        repository.load_positions(
            BrokerAccount(
                broker="SINOPAC",
                account_ref="A",
            )
        )

    assert (
        "effective_at DESC" in connection.last[0]
        and "recorded_at DESC" in connection.last[0]
        and "snapshot_id DESC" in connection.last[0]
    )

    repository.as_of(
        "SINOPAC",
        "A",
        __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ),
    )

    assert "effective_at<=%s" in connection.last[0]
    assert connection.commits == 0


class _ReturningCursor(_Cursor):
    def fetchone(self):
        return (1,)


class _ReturningConnection(_Connection):
    def __init__(self):
        super().__init__(); self.statements = []

    def cursor(self):
        connection = self
        class Cursor(_ReturningCursor):
            def execute(self, sql, params=None):
                connection.last = (sql, params)
                connection.statements.append((sql, params))
        return Cursor(self)


def _broker_attempt() -> BrokerActionAttempt:
    return BrokerActionAttempt(
        attempt_id="ATTEMPT-1", broker="SINOPAC", account_ref="A",
        order_id="ORDER-1", action=BrokerActionKind.SUBMIT,
        broker_client_order_ref="CLIENT-1", command_id="COMMAND-1",
        correlation_id="CORR-1", authorization_id="AUTH-1",
        created_at=__import__("datetime").datetime(
            2026, 9, 27, tzinfo=__import__("datetime").timezone.utc
        ),
    )


def test_broker_action_postgres_conditional_writes_encode_retry_eligibility() -> None:
    connection = _ReturningConnection()
    repository = PostgresBrokerActionRepository(connection)
    item = _broker_attempt()

    repository.reserve_head(item, expected_version=3)
    reserve_sql, reserve_params = connection.last
    assert "unresolved_attempt_id IS NULL" in reserve_sql
    assert "automatic_invocation_eligible=TRUE" in reserve_sql
    assert "automatic_invocation_eligible=FALSE" in reserve_sql
    assert reserve_params[-1] == 3

    material_sql = None
    for kind in (
        BrokerActionResolutionKind.SUCCEEDED,
        BrokerActionResolutionKind.FAILED,
    ):
        repository.resolve_head(item, resolution_kind=kind, expected_version=4)
        current_sql, material_params = connection.last
        assert "unresolved_attempt_id=NULL" in current_sql
        assert "automatic_invocation_eligible=%s" in current_sql
        assert material_params[0] is False
        material_sql = current_sql

    repository.resolve_head(
        item, resolution_kind=BrokerActionResolutionKind.NOT_DISPATCHED,
        expected_version=5,
    )
    retry_sql, retry_params = connection.last
    assert retry_sql == material_sql
    assert retry_params[0] is True
    assert connection.commits == 0


def test_broker_action_migration_encodes_durable_eligibility_without_manual_override() -> None:
    sql = Path(
        "persistence/postgres/migrations/0006_broker_action_safety.sql"
    ).read_text(encoding="utf-8")
    assert "automatic_invocation_eligible BOOLEAN NOT NULL DEFAULT FALSE" in sql
    assert "unresolved_attempt_id IS NULL OR automatic_invocation_eligible = FALSE" in sql
    assert "NOT_DISPATCHED" in sql
    assert "manual_override" not in sql.lower()
