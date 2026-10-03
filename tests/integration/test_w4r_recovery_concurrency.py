from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from persistence.broker_recovery import (
    AccountRecoveryControl,
    BrokerReportInboxEntry,
    BrokerReportIngressStatus,
    RecoveryFenceConflictError,
)
from persistence.postgres.broker_recovery import PostgresBrokerRecoveryRepository
from persistence.postgres.compatibility import detect_postgres_major
from persistence.postgres.driver import connect_postgres
from persistence.postgres.migrations import discover_migrations, run_migrations
from persistence.postgres.readiness_fence import (
    PostgresRecoveryReadinessFenceRepository,
)
from trading.account import BrokerAccount


_TARGETS = ((17, "POSTGRES17_TEST_DSN"), (18, "POSTGRES18_TEST_DSN"))
_MIGRATION_DIRECTORY = Path("persistence/postgres/migrations")
_LOCK_NOT_AVAILABLE = "55P03"


def _connect_verified_test_database(major: int, variable: str):
    """只連向明示 TEST_DSN，並在寫入測試資料前驗證 server major。"""

    dsn = os.environ.get(variable)
    if not dsn:
        pytest.skip(f"{variable} is not configured; W4R concurrency remains PENDING")
    connection = connect_postgres(dsn)
    try:
        assert connection.autocommit is False
        with connection.cursor() as cursor:
            cursor.execute("SHOW server_version_num")
            assert detect_postgres_major(int(cursor.fetchone()[0])) == major
        return connection
    except BaseException:
        connection.close()
        raise


def _prepare_schema(major: int, variable: str) -> None:
    """在授權的測試資料庫套用既有 migration chain；不改寫 migration source。"""

    connection = _connect_verified_test_database(major, variable)
    try:
        migrations = discover_migrations(_MIGRATION_DIRECTORY)
        assert migrations and migrations[-1].version == 9
        run_migrations(connection, migrations)
        connection.commit()
    finally:
        connection.close()


def _account(major: int, scenario: str) -> BrokerAccount:
    return BrokerAccount(
        broker="CODEX_W4R_TEST",
        account_ref=f"W4R-PG{major}-{scenario}-{uuid4().hex}",
    )


def _control(
    account: BrokerAccount,
    *,
    ingress_version: int,
    readiness_revision: int,
    active: bool,
) -> AccountRecoveryControl:
    return AccountRecoveryControl(
        broker=account.broker,
        account_ref=account.account_ref,
        generation=1,
        recovery_cut_revision=7,
        ingress_version=ingress_version,
        readiness_revision=readiness_revision,
        active=active,
        recorded_at=datetime.now(timezone.utc),
    )


def _entry(account: BrokerAccount) -> BrokerReportInboxEntry:
    return BrokerReportInboxEntry(
        ingress_id=f"INGRESS-{uuid4().hex}",
        broker=account.broker,
        account_ref=account.account_ref,
        generation=1,
        received_at=datetime.now(timezone.utc),
        report_type="ORDER_STATUS",
        payload_fingerprint=f"FP-{uuid4().hex}",
        payload_json={"source": "W4R_POSTGRES_CONCURRENCY_TEST"},
    )


def _cleanup(major: int, variable: str, account: BrokerAccount) -> None:
    """只刪除本測試唯一 BrokerAccount 的 material；不得 truncate 共用資料表。"""

    connection = _connect_verified_test_database(major, variable)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM trading.broker_report_applications a "
                "USING trading.broker_report_inbox i "
                "WHERE a.ingress_id=i.ingress_id AND i.broker=%s AND i.account_ref=%s",
                (account.broker, account.account_ref),
            )
            cursor.execute(
                "DELETE FROM trading.broker_report_inbox WHERE broker=%s AND account_ref=%s",
                (account.broker, account.account_ref),
            )
            cursor.execute(
                "DELETE FROM trading.account_recovery_controls WHERE broker=%s AND account_ref=%s",
                (account.broker, account.account_ref),
            )
        connection.commit()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT "
                "(SELECT COUNT(*) FROM trading.account_recovery_controls "
                " WHERE broker=%s AND account_ref=%s), "
                "(SELECT COUNT(*) FROM trading.broker_report_inbox "
                " WHERE broker=%s AND account_ref=%s)",
                (
                    account.broker,
                    account.account_ref,
                    account.broker,
                    account.account_ref,
                ),
            )
            assert cursor.fetchone() == (0, 0)
    finally:
        connection.close()


def _rollback_and_close(connection) -> None:
    if connection is not None:
        try:
            connection.rollback()
        finally:
            connection.close()


@pytest.mark.parametrize(("major", "variable"), _TARGETS)
def test_handoff_lock_serializes_ingress_and_post_handoff_capture(
    major: int, variable: str
) -> None:
    """真實 row lock 必須排除 concurrent ingress，handoff 後 evidence 只能 inactive capture。"""

    _prepare_schema(major, variable)
    account = _account(major, "LOCK")
    entry = _entry(account)
    setup = lock_connection = ingress_connection = inspect_connection = None
    try:
        setup = _connect_verified_test_database(major, variable)
        PostgresBrokerRecoveryRepository(setup).begin_recovery(
            _control(account, ingress_version=0, readiness_revision=0, active=True),
            expected_generation=0,
        )
        setup.commit()

        lock_connection = _connect_verified_test_database(major, variable)
        token = PostgresRecoveryReadinessFenceRepository(lock_connection).lock_active(
            account
        )
        assert token is not None
        assert token.captured_readiness_revision == 0

        ingress_connection = _connect_verified_test_database(major, variable)
        with ingress_connection.cursor() as cursor:
            cursor.execute("SET LOCAL lock_timeout = '250ms'")
        with pytest.raises(Exception) as lock_error:
            PostgresBrokerRecoveryRepository(ingress_connection).append_inbox(entry)
        assert getattr(lock_error.value, "sqlstate", None) == _LOCK_NOT_AVAILABLE
        ingress_connection.rollback()
        with ingress_connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM trading.broker_report_inbox WHERE ingress_id=%s",
                (entry.ingress_id,),
            )
            assert cursor.fetchone()[0] == 0

        completed = _control(
            account, ingress_version=0, readiness_revision=0, active=False
        )
        PostgresBrokerRecoveryRepository(lock_connection).finalize_handoff(
            completed,
            expected_generation=1,
            expected_ingress_version=0,
            expected_readiness_revision=0,
        )
        lock_connection.commit()

        assert (
            PostgresBrokerRecoveryRepository(ingress_connection).append_inbox(entry)
            is BrokerReportIngressStatus.APPENDED
        )
        ingress_connection.commit()

        inspect_connection = _connect_verified_test_database(major, variable)
        with inspect_connection.cursor() as cursor:
            cursor.execute(
                "SELECT generation,ingress_version,readiness_revision,active "
                "FROM trading.account_recovery_controls WHERE broker=%s AND account_ref=%s",
                (account.broker, account.account_ref),
            )
            assert cursor.fetchone() == (1, 0, 0, False)
            cursor.execute(
                "SELECT recovery_active_at_capture FROM trading.broker_report_inbox "
                "WHERE ingress_id=%s",
                (entry.ingress_id,),
            )
            assert cursor.fetchone() == (False,)
    finally:
        for connection in (
            inspect_connection,
            ingress_connection,
            lock_connection,
            setup,
        ):
            _rollback_and_close(connection)
        _cleanup(major, variable, account)


@pytest.mark.parametrize(("major", "variable"), _TARGETS)
def test_readiness_cas_rejects_stale_handoff_and_accepts_fresh_revision(
    major: int, variable: str
) -> None:
    """readiness revision 是 handoff CAS authority；stale token 不得使 control inactive。"""

    _prepare_schema(major, variable)
    account = _account(major, "CAS")
    setup = advance_connection = stale_connection = fresh_connection = inspect = None
    try:
        setup = _connect_verified_test_database(major, variable)
        initial = _control(
            account, ingress_version=3, readiness_revision=0, active=True
        )
        PostgresBrokerRecoveryRepository(setup).begin_recovery(
            initial, expected_generation=0
        )
        setup.commit()

        advance_connection = _connect_verified_test_database(major, variable)
        fence = PostgresRecoveryReadinessFenceRepository(advance_connection)
        token = fence.lock_active(account)
        assert token is not None
        advanced = fence.advance_locked(token)
        assert advanced.captured_readiness_revision == 1
        advance_connection.commit()

        stale_connection = _connect_verified_test_database(major, variable)
        with pytest.raises(RecoveryFenceConflictError):
            PostgresBrokerRecoveryRepository(stale_connection).finalize_handoff(
                initial.model_copy(update={"active": False}),
                expected_generation=1,
                expected_ingress_version=3,
                expected_readiness_revision=0,
            )
        stale_connection.rollback()

        inspect = _connect_verified_test_database(major, variable)
        current = PostgresBrokerRecoveryRepository(inspect).get_control(account)
        assert current is not None
        assert current.active is True
        assert (
            current.generation,
            current.recovery_cut_revision,
            current.ingress_version,
            current.readiness_revision,
        ) == (1, 7, 3, 1)
        inspect.rollback()
        inspect.close()
        inspect = None

        fresh_connection = _connect_verified_test_database(major, variable)
        PostgresBrokerRecoveryRepository(fresh_connection).finalize_handoff(
            current.model_copy(
                update={"active": False, "recorded_at": datetime.now(timezone.utc)}
            ),
            expected_generation=1,
            expected_ingress_version=3,
            expected_readiness_revision=1,
        )
        fresh_connection.commit()

        inspect = _connect_verified_test_database(major, variable)
        finalized = PostgresBrokerRecoveryRepository(inspect).get_control(account)
        assert finalized is not None
        assert finalized.active is False
        assert (
            finalized.generation,
            finalized.recovery_cut_revision,
            finalized.ingress_version,
            finalized.readiness_revision,
        ) == (1, 7, 3, 1)
    finally:
        for connection in (
            inspect,
            fresh_connection,
            stale_connection,
            advance_connection,
            setup,
        ):
            _rollback_and_close(connection)
        _cleanup(major, variable, account)
