import ast
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from persistence.account import (
    AccountPositionSnapshot,
    ExpectedSnapshotIntegrityError,
    ExpectedStateBaselineNotEstablishedError,
    ExpectedStateKind,
    ExpectedStateRead,
    ExpectedStateReadError,
)
from persistence.postgres.account import (
    PostgresExpectedPositionSnapshotRepository,
)
from trading.account import (
    AccountPosition,
    BrokerAccount,
    PositionDirection,
)


NOW = datetime(2026, 9, 26, 8, tzinfo=timezone.utc)
ACCOUNT = BrokerAccount(
    broker="SINOPAC",
    account_ref="A",
)


def _position() -> AccountPosition:
    return AccountPosition(
        broker="SINOPAC",
        account_ref="A",
        instrument_id=1,
        contract_id=101,
        direction=PositionDirection.LONG,
        quantity=2,
    )


def _snapshot(
    positions: tuple[AccountPosition, ...] = (),
    *,
    broker: str = "SINOPAC",
    account_ref: str = "A",
) -> AccountPositionSnapshot:
    return AccountPositionSnapshot(
        snapshot_id="SNAP-1",
        broker=broker,
        account_ref=account_ref,
        effective_at=NOW,
        recorded_at=NOW,
        source_event_id="EVENT-1",
        positions=positions,
    )


class _Cursor:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params=None):
        self.connection.last = (sql, params)

        if self.connection.execute_error is not None:
            raise self.connection.execute_error

    def fetchone(self):
        return self.connection.row


class _Connection:
    def __init__(
        self,
        *,
        row=None,
        execute_error: Exception | None = None,
    ):
        self.row = row
        self.execute_error = execute_error
        self.last = None

    def cursor(self):
        return _Cursor(self)


def _repository_for_snapshot(
    snapshot: AccountPositionSnapshot,
) -> PostgresExpectedPositionSnapshotRepository:
    return PostgresExpectedPositionSnapshotRepository(
        _Connection(
            row=(snapshot.model_dump_json(),),
        )
    )


def test_explicit_empty_snapshot_is_authoritative_flat() -> None:
    repository = _repository_for_snapshot(
        _snapshot(())
    )

    result = repository.read_expected_state(ACCOUNT)

    assert result.state is ExpectedStateKind.EXPLICIT_FLAT
    assert result.snapshot_id == "SNAP-1"
    assert result.positions == ()
    assert repository.load_positions(ACCOUNT) == ()


def test_non_empty_snapshot_is_authoritative_expected_positions() -> None:
    position = _position()
    repository = _repository_for_snapshot(
        _snapshot((position,))
    )

    result = repository.read_expected_state(ACCOUNT)

    assert result.state is ExpectedStateKind.EXPECTED_POSITIONS
    assert result.snapshot_id == "SNAP-1"
    assert result.positions == (position,)
    assert repository.load_positions(ACCOUNT) == (position,)


def test_not_initialized_is_representable_but_not_inferred_from_missing_row() -> None:
    result = ExpectedStateRead.not_initialized(
        broker="SINOPAC",
        account_ref="A",
    )

    assert result.state is ExpectedStateKind.NOT_INITIALIZED
    assert result.snapshot_id is None
    assert result.positions == ()

    repository = PostgresExpectedPositionSnapshotRepository(
        _Connection(row=None)
    )

    with pytest.raises(
        ExpectedStateBaselineNotEstablishedError,
        match="baseline is not established",
    ):
        repository.read_expected_state(ACCOUNT)


def test_expected_state_result_is_immutable_and_exact() -> None:
    result = ExpectedStateRead.not_initialized(
        broker="SINOPAC",
        account_ref="A",
    )

    with pytest.raises(ValidationError):
        result.state = ExpectedStateKind.EXPLICIT_FLAT

    with pytest.raises(
        ValidationError,
        match="NOT_INITIALIZED",
    ):
        ExpectedStateRead(
            state=ExpectedStateKind.NOT_INITIALIZED,
            broker="SINOPAC",
            account_ref="A",
            snapshot_id="SNAP",
            positions=(),
        )

    with pytest.raises(
        ValidationError,
        match="EXPLICIT_FLAT",
    ):
        ExpectedStateRead(
            state=ExpectedStateKind.EXPLICIT_FLAT,
            broker="SINOPAC",
            account_ref="A",
            snapshot_id="SNAP",
            positions=(_position(),),
        )

    with pytest.raises(
        ValidationError,
        match="EXPECTED_POSITIONS",
    ):
        ExpectedStateRead(
            state=ExpectedStateKind.EXPECTED_POSITIONS,
            broker="SINOPAC",
            account_ref="A",
            snapshot_id="SNAP",
            positions=(),
        )


def test_missing_snapshot_never_falls_back_to_flat_positions() -> None:
    repository = PostgresExpectedPositionSnapshotRepository(
        _Connection(row=None)
    )

    with pytest.raises(
        ExpectedStateBaselineNotEstablishedError
    ):
        repository.load_positions(ACCOUNT)


def test_repository_read_failure_is_typed_and_not_domain_state() -> None:
    repository = PostgresExpectedPositionSnapshotRepository(
        _Connection(
            execute_error=RuntimeError("database unavailable"),
        )
    )

    with pytest.raises(
        ExpectedStateReadError,
        match="snapshot read failed",
    ) as exc_info:
        repository.read_expected_state(ACCOUNT)

    assert not isinstance(
        exc_info.value,
        ExpectedStateBaselineNotEstablishedError,
    )


@pytest.mark.parametrize(
    "payload",
    [
        '{"invalid":"snapshot"}',
        '{"snapshot_id":',
    ],
)
def test_malformed_snapshot_is_typed_integrity_failure(
    payload: str,
) -> None:
    repository = PostgresExpectedPositionSnapshotRepository(
        _Connection(
            row=(payload,),
        )
    )

    with pytest.raises(
        ExpectedSnapshotIntegrityError,
        match="canonical decode",
    ):
        repository.read_expected_state(ACCOUNT)


def test_snapshot_payload_scope_mismatch_is_integrity_failure() -> None:
    snapshot = _snapshot(
        (),
        broker="SINOPAC",
        account_ref="OTHER",
    )

    repository = _repository_for_snapshot(snapshot)

    with pytest.raises(
        ExpectedSnapshotIntegrityError,
        match="account scope mismatch",
    ):
        repository.read_expected_state(ACCOUNT)


def test_c01_does_not_absorb_later_authority_primitives() -> None:
    """檢查實際 Python authority symbols，不掃描 comment/docstring 純文字。"""

    forbidden_symbols = {
        "AccountStateHead",
        "AccountRecoveryCheckpoint",
        "RecoveryCut",
        "EXPECTED_STATE_INITIALIZED",
    }

    for path in (
        "persistence/account.py",
        "persistence/postgres/account.py",
    ):
        tree = ast.parse(
            Path(path).read_text(encoding="utf-8"),
            filename=path,
        )

        defined_or_imported_symbols: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(
                node,
                (
                    ast.ClassDef,
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                defined_or_imported_symbols.add(node.name)

            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined_or_imported_symbols.add(target.id)

            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    defined_or_imported_symbols.add(node.target.id)

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    defined_or_imported_symbols.add(
                        alias.asname
                        or alias.name.rsplit(".", 1)[-1]
                    )

        assert forbidden_symbols.isdisjoint(
            defined_or_imported_symbols
        ), (
            f"{path} absorbed later authority symbols: "
            f"{forbidden_symbols & defined_or_imported_symbols}"
        )
