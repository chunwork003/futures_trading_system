import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

from persistence.events import EventAppendStatus, TradingEvent
from persistence.postgres.compatibility import detect_postgres_major
from persistence.postgres.driver import connect_postgres
from persistence.postgres.event_ledger import PostgresEventLedgerRepository
from persistence.postgres.migrations import discover_migrations, run_migrations


@pytest.mark.parametrize(("major", "variable"), [(17, "POSTGRES17_TEST_DSN"), (18, "POSTGRES18_TEST_DSN")])
def test_postgres_migration_event_and_rollback_smoke(major: int, variable: str) -> None:
    dsn = os.environ.get(variable)
    if not dsn:
        pytest.skip(f"{variable} is not configured; compatibility remains PENDING")
    connection = connect_postgres(dsn)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW server_version_num")
            assert detect_postgres_major(int(cursor.fetchone()[0])) == major
        run_migrations(connection, discover_migrations(Path("persistence/postgres/migrations")))
        repository = PostgresEventLedgerRepository(connection)
        event = TradingEvent(
            event_id=f"PG{major}-SMOKE", event_type="SMOKE", source="INTEGRATION",
            entity_type="TEST", entity_id=f"PG{major}", occurred_at=datetime.now(timezone.utc),
            received_at=datetime.now(timezone.utc), sequence=0, event_version=1,
            idempotency_scope="PG-SMOKE", idempotency_key=f"PG{major}-SMOKE", payload_json={},
        )
        assert repository.append(event).status is EventAppendStatus.APPENDED
    finally:
        connection.rollback()
        connection.close()
