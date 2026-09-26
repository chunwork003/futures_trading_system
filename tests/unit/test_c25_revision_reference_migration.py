
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from domain.market_observation import (
    MarketObservationRevisionId,
)
from persistence.postgres.market_observation import (
    PostgresMarketObservationAcceptanceRepository,
)
from persistence.postgres.strategy_state import (
    PostgresStrategyStateRepository,
)
from persistence.strategy_state import (
    LegacyMarketObservationReferenceError,
    StrategyStateReferenceConflictError,
    StrategyStateSnapshot,
)


NOW = datetime(
    2026,
    9,
    26,
    4,
    tzinfo=timezone.utc,
)

MOR1_A = "mor1_" + ("a" * 64)
MOR1_B = "mor1_" + ("b" * 64)


def snapshot():
    return StrategyStateSnapshot(
        snapshot_id="SS-C25",
        strategy_instance_id="SI-1",
        strategy_id="EMA_CROSS",
        strategy_version="1.0.0",
        config_version="C1",
        config_fingerprint=(
            "f" * 64
        ),
        instrument_id=1,
        timeframe="1m",
        state_schema_version=1,
        last_market_observation_revision_id=(
            MOR1_A
        ),
        captured_at=NOW,
        state_json={
            "schema_version": 1,
            "previous_ema20": 1.0,
            "previous_ema60": 2.0,
        },
    )


class Cursor:
    def __init__(
        self,
        connection,
    ):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(
        self,
        *args,
    ):
        return False

    def execute(
        self,
        sql,
        params=None,
    ):
        self.connection.calls.append(
            (
                " ".join(
                    sql.split()
                ),
                params,
            )
        )

    def fetchone(self):
        if not self.connection.rows:
            return None

        return (
            self.connection.rows.pop(
                0
            )
        )


class Connection:
    def __init__(
        self,
        rows=(),
    ):
        self.rows = list(
            rows
        )
        self.calls = []

    def cursor(self):
        return Cursor(
            self
        )


def test_0004_is_non_destructive_revision_reference_migration():
    sql = Path(
        "persistence/postgres/migrations/"
        "0004_strategy_market_observation_revision_ref.sql"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "ADD COLUMN "
        "last_market_observation_revision_id TEXT"
        in sql
    )

    assert (
        "REFERENCES "
        "trading.market_observation_revisions"
        in sql
    )

    assert (
        "last_market_observation_id"
        in sql
    )

    assert (
        "last_market_observation_revision_id"
        in sql
    )

    assert (
        "mor1_[0-9a-f]{64}"
        in sql
    )

    for term in (
        "??",
        "??",
        "??",
        "??",
    ):
        assert term in sql

    for forbidden in (
        "UPDATE trading.strategy_state_snapshots",
        "DELETE FROM",
        "DROP TABLE",
        "DROP COLUMN",
        "INSERT INTO",
    ):
        assert forbidden not in sql


def test_postgres_writer_mirrors_exact_canonical_value():
    item = snapshot()
    connection = Connection()

    PostgresStrategyStateRepository(
        connection
    ).append(
        item
    )

    sql, params = (
        connection.calls[0]
    )

    assert (
        "last_market_observation_id"
        in sql
    )

    assert (
        "last_market_observation_revision_id"
        in sql
    )

    assert params[10] == MOR1_A
    assert params[11] == MOR1_A


def test_legacy_only_persisted_row_cannot_recover():
    connection = Connection(
        rows=[
            (
                MOR1_A,
                None,
                snapshot().model_dump_json(),
            )
        ]
    )

    with pytest.raises(
        LegacyMarketObservationReferenceError,
        match="legacy-only",
    ):
        PostgresStrategyStateRepository(
            connection
        ).latest(
            "SI-1"
        )


def test_persisted_legacy_canonical_disagreement_is_typed_failure():
    connection = Connection(
        rows=[
            (
                MOR1_A,
                MOR1_B,
                snapshot().model_dump_json(),
            )
        ]
    )

    with pytest.raises(
        StrategyStateReferenceConflictError,
        match="disagree",
    ):
        PostgresStrategyStateRepository(
            connection
        ).latest(
            "SI-1"
        )


def test_exact_persisted_reference_restores_snapshot():
    item = snapshot()

    connection = Connection(
        rows=[
            (
                MOR1_A,
                MOR1_A,
                item.model_dump_json(),
            )
        ]
    )

    restored = (
        PostgresStrategyStateRepository(
            connection
        ).latest(
            "SI-1"
        )
    )

    assert restored == item


def test_public_revision_read_is_exact_and_missing_returns_none():
    connection = Connection(
        rows=[
            None,
        ]
    )

    repository = (
        PostgresMarketObservationAcceptanceRepository(
            connection
        )
    )

    result = repository.get_revision(
        MarketObservationRevisionId(
            MOR1_A
        )
    )

    assert result is None

    assert (
        len(connection.calls)
        == 1
    )

    sql, params = (
        connection.calls[0]
    )

    assert (
        "WHERE observation_revision_id=%s"
        in sql
    )

    assert params == (
        MOR1_A,
    )


def test_strategy_repository_has_no_commit_rollback_or_latest_repair():
    source = Path(
        "persistence/postgres/"
        "strategy_state.py"
    ).read_text(
        encoding="utf-8"
    )

    assert ".commit(" not in source
    assert ".rollback(" not in source
    assert (
        "market_observation_heads"
        not in source
    )

    assert (
        "MAX(revision_seq)"
        not in source
    )


def test_0004_does_not_backfill_or_fabricate_legacy_ids():
    sql = Path(
        "persistence/postgres/migrations/"
        "0004_strategy_market_observation_revision_ref.sql"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "UPDATE "
        "trading.strategy_state_snapshots"
        not in sql
    )

    assert (
        "SET "
        "last_market_observation_revision_id"
        not in sql
    )

    assert "BAR-" not in sql


def test_snapshot_rejects_arbitrary_bar_id():
    item = snapshot()

    values = item.model_dump(
        exclude={
            "last_market_observation_revision_id"
        }
    )

    values[
        "last_market_observation_id"
    ] = "BAR-1"

    with pytest.raises(
        ValidationError,
        match="mor1",
    ):
        StrategyStateSnapshot(
            **values
        )
