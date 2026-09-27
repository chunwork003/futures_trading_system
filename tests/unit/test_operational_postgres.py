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
from persistence.broker_recovery import (
    AccountRecoveryControl,
    BrokerReportApplication,
    BrokerReportApplicationStatus,
    BrokerReportConflictError,
    BrokerReportInboxEntry,
    RecoveryFenceConflictError,
)
from persistence.postgres.broker_recovery import PostgresBrokerRecoveryRepository
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


def test_broker_recovery_migration_separates_inbox_control_and_continuity() -> None:
    sql = Path(
        "persistence/postgres/migrations/0007_broker_recovery_evidence.sql"
    ).read_text(encoding="utf-8")
    for table in (
        "broker_report_inbox",
        "broker_report_applications",
        "account_recovery_controls",
        "execution_continuity_epochs",
        "broker_sequence_gaps",
    ):
        assert f"CREATE TABLE trading.{table}" in sql
        assert f"COMMENT ON TABLE trading.{table}" in sql
    assert "TIMESTAMPTZ" in sql
    assert "JSONB" in sql
    assert "account_state_heads" not in sql
    assert "recovery_active_at_capture BOOLEAN NOT NULL" in sql
    assert "application_sequence BIGINT NOT NULL" in sql
    assert "UNIQUE (ingress_id, generation, application_sequence)" in sql
    assert "FOREIGN KEY (ingress_id, generation)" in sql


def test_broker_recovery_handoff_is_one_conditional_write_without_commit() -> None:
    connection = _ReturningConnection()
    repository = PostgresBrokerRecoveryRepository(connection)
    control = AccountRecoveryControl(
        broker="SINOPAC",
        account_ref="A",
        generation=4,
        recovery_cut_revision=8,
        ingress_version=12,
        active=False,
        recorded_at=__import__("datetime").datetime(
            2026, 9, 27, tzinfo=__import__("datetime").timezone.utc
        ),
    )

    repository.finalize_handoff(
        control,
        expected_generation=4,
        expected_ingress_version=12,
    )

    sql, params = connection.last
    assert "generation=%s" in sql
    assert "recovery_cut_revision=%s" in sql
    assert "ingress_version=%s" in sql
    assert "active=TRUE" in sql
    assert "NOT EXISTS" in sql
    assert params[1:] == ("SINOPAC", "A", 4, 8, 12)
    assert connection.commits == 0


class _QueueConnection(_Connection):
    def __init__(self, rows):
        super().__init__(); self.rows=list(rows); self.statements=[]
    def cursor(self):
        connection=self
        class Cursor(_Cursor):
            def execute(self, sql, params=None):
                connection.last=(sql,params); connection.statements.append((sql,params))
            def fetchone(self):
                return connection.rows.pop(0)
        return Cursor(self)


def _recovery_entry():
    return BrokerReportInboxEntry(
        ingress_id="IN-1",broker="SINOPAC",account_ref="A",generation=4,
        received_at=__import__("datetime").datetime(2026,9,27,tzinfo=__import__("datetime").timezone.utc),
        report_type="ORDER",payload_fingerprint="FP-1",payload_json={"status":"Submitted"},
    )


def test_postgres_new_ingress_locks_control_and_atomically_advances_frontier_once() -> None:
    connection=_QueueConnection([(4,12,True),("IN-1",),(13,)])
    repository=PostgresBrokerRecoveryRepository(connection)
    repository.append_inbox(_recovery_entry())
    sqls=[sql for sql,_ in connection.statements]
    assert "FOR UPDATE" in sqls[0]
    assert "recovery_active_at_capture" in sqls[1]
    assert "ingress_version=ingress_version+1" in sqls[2]
    assert "active=TRUE" in sqls[2]
    assert connection.commits == 0


def test_postgres_duplicate_ingress_does_not_advance_frontier() -> None:
    entry=_recovery_entry()
    connection=_QueueConnection([(4,12,True),None,(entry.model_dump(mode="json"),)])
    repository=PostgresBrokerRecoveryRepository(connection)
    repository.append_inbox(entry)
    assert not any("ingress_version=ingress_version+1" in sql for sql,_ in connection.statements)
    assert connection.commits == 0


def test_postgres_inactive_control_accepts_only_same_generation_without_frontier_advance() -> None:
    entry=_recovery_entry()
    connection=_QueueConnection([(4,12,False),("IN-1",)])
    repository=PostgresBrokerRecoveryRepository(connection)
    repository.append_inbox(entry)
    assert not any("ingress_version=ingress_version+1" in sql for sql,_ in connection.statements)
    wrong=_QueueConnection([(5,12,False)])
    with pytest.raises(RecoveryFenceConflictError,match="stale"):
        PostgresBrokerRecoveryRepository(wrong).append_inbox(entry)
    assert not any("broker_report_inbox" in sql and "INSERT" in sql for sql,_ in wrong.statements)


def test_postgres_application_identity_is_idempotent_and_sequence_is_durable() -> None:
    application=BrokerReportApplication(
        application_id="APP-1",ingress_id="IN-1",generation=4,
        application_sequence=2,status=BrokerReportApplicationStatus.APPLIED,
        recorded_at=__import__("datetime").datetime(2026,9,27,tzinfo=__import__("datetime").timezone.utc),
        evidence=("exact current disposition",),
    )
    connection=_QueueConnection([(4,),None,(1,)])
    PostgresBrokerRecoveryRepository(connection).append_application(application)
    assert "broker_report_inbox" in connection.statements[0][0]
    assert "FOR UPDATE" in connection.statements[0][0]
    assert "MAX(application_sequence)" in connection.statements[2][0]
    assert "application_json" in connection.statements[3][0]
    assert connection.commits == 0


def test_postgres_application_duplicate_and_sequence_conflicts_fail_closed() -> None:
    application=BrokerReportApplication(
        application_id="APP-1",ingress_id="IN-1",generation=4,
        application_sequence=1,status=BrokerReportApplicationStatus.APPLIED,
        recorded_at=__import__("datetime").datetime(2026,9,27,tzinfo=__import__("datetime").timezone.utc),
        evidence=("exact current disposition",),
    )
    duplicate=_QueueConnection([(4,),(application.model_dump(mode="json"),)])
    PostgresBrokerRecoveryRepository(duplicate).append_application(application)
    assert len(duplicate.statements)==2 and duplicate.commits==0

    gap=_QueueConnection([(4,),None,(1,)])
    with pytest.raises(BrokerReportConflictError,match="contiguous"):
        PostgresBrokerRecoveryRepository(gap).append_application(
            application.model_copy(update={"application_id":"APP-3","application_sequence":3})
        )
    assert not any("INSERT INTO trading.broker_report_applications" in sql for sql,_ in gap.statements)


def test_postgres_handoff_uses_exact_generation_latest_sequence_not_timestamp() -> None:
    connection=_ReturningConnection()
    repository=PostgresBrokerRecoveryRepository(connection)
    control=AccountRecoveryControl(
        broker="SINOPAC",account_ref="A",generation=4,recovery_cut_revision=8,
        ingress_version=12,active=False,
        recorded_at=__import__("datetime").datetime(2026,9,27,tzinfo=__import__("datetime").timezone.utc),
    )
    repository.finalize_handoff(control,expected_generation=4,expected_ingress_version=12)
    sql,_=connection.last
    assert "a.generation=i.generation" in sql
    assert "newer.application_sequence>a.application_sequence" in sql
    assert "recorded_at>" not in sql


def test_local_recovery_migration_scopes_reconciliation_cases_without_backfill() -> None:
    sql=Path("persistence/postgres/migrations/0008_local_recovery_reconciliation.sql").read_text(encoding="utf-8")
    assert "ADD COLUMN broker TEXT" in sql
    assert "ADD COLUMN account_ref TEXT" in sql
    assert "enforce_reconciliation_case_scope" in sql
    assert "reconciliation_case_account_latest_idx" in sql
    assert "UPDATE trading.reconciliation_case_history" not in sql
    assert "COMMENT ON COLUMN trading.reconciliation_case_history.broker" in sql
