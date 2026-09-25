from pathlib import Path

from persistence.postgres.account import PostgresExpectedPositionSnapshotRepository
from trading.account import BrokerAccount


def test_operational_migration_has_separate_tables_and_required_types_comments() -> None:
    sql=Path("persistence/postgres/migrations/0002_operational_persistence.sql").read_text(encoding="utf-8")
    tables=("orders","fills","expected_position_snapshots","expected_position_snapshot_items","broker_position_observations","broker_position_observation_items","account_snapshots","reconciliation_case_history","strategy_instances","strategy_state_snapshots")
    for table in tables:
        assert f"CREATE TABLE trading.{table}" in sql
        assert f"COMMENT ON TABLE trading.{table}" in sql
    for token in ("NUMERIC","TIMESTAMPTZ","JSONB","PRIMARY KEY","UNIQUE","CHECK"):
        assert token in sql
    assert "event_ledger" not in "\n".join(line for line in sql.splitlines() if line.startswith("CREATE TABLE"))


def test_expected_and_actual_storage_are_structurally_separate() -> None:
    sql=Path("persistence/postgres/migrations/0002_operational_persistence.sql").read_text(encoding="utf-8")
    assert "trading.expected_position_snapshots" in sql
    assert "trading.broker_position_observations" in sql
    assert "UPDATE trading.reconciliation_case_history" not in sql
    assert "DELETE FROM" not in sql


class _Cursor:
    def __init__(self, connection): self.connection=connection
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def execute(self,sql,params=None): self.connection.last=(sql,params)
    def fetchone(self): return None
class _Connection:
    def __init__(self): self.last=None; self.commits=0
    def cursor(self): return _Cursor(self)
    def commit(self): self.commits+=1


def test_expected_repository_latest_as_of_order_and_loader_compatibility() -> None:
    connection=_Connection(); repository=PostgresExpectedPositionSnapshotRepository(connection)
    assert repository.load_positions(BrokerAccount(broker="SINOPAC",account_ref="A")) == ()
    assert "effective_at DESC, recorded_at DESC, snapshot_id DESC" in connection.last[0]
    repository.as_of("SINOPAC","A",__import__("datetime").datetime.now(__import__("datetime").timezone.utc))
    assert "effective_at<=%s" in connection.last[0]
    assert connection.commits == 0
