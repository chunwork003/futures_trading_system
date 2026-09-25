from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from persistence.contracts import (
    AppendOnlyRepository,
    PersistenceContractError,
    SnapshotRepository,
    UnitOfWork,
    normalize_aware_utc,
    normalize_stable_id,
    require_exact_decimal,
)


def test_stable_id_normalizes_and_rejects_invalid_values() -> None:
    assert normalize_stable_id(" EVT-1 ") == "EVT-1"
    for value in ("", "   ", None, 1):
        with pytest.raises(PersistenceContractError):
            normalize_stable_id(value)  # type: ignore[arg-type]


def test_exact_decimal_accepts_finite_decimal_only() -> None:
    assert require_exact_decimal(Decimal("1.230")) == Decimal("1.230")
    for value in (1.0, 1, Decimal("NaN"), Decimal("Infinity")):
        with pytest.raises(PersistenceContractError):
            require_exact_decimal(value)  # type: ignore[arg-type]


def test_aware_datetime_normalizes_utc_and_rejects_naive() -> None:
    value = datetime(2026, 9, 25, 9, 0, tzinfo=timezone(timedelta(hours=8)))
    assert normalize_aware_utc(value) == datetime(2026, 9, 25, 1, 0, tzinfo=timezone.utc)
    with pytest.raises(PersistenceContractError):
        normalize_aware_utc(datetime(2026, 9, 25, 9, 0))


def test_protocols_are_runtime_checkable_and_do_not_define_generic_crud() -> None:
    class Append:
        def append(self, record): return None

    class Snapshots:
        def append_snapshot(self, snapshot): return None
        def latest(self, key): return None
        def as_of(self, key, at): return None

    class Work:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, traceback): return False
        def commit(self): return None
        def rollback(self): return None

    assert isinstance(Append(), AppendOnlyRepository)
    assert isinstance(Snapshots(), SnapshotRepository)
    assert isinstance(Work(), UnitOfWork)
    for forbidden in ("update", "delete"):
        assert forbidden not in AppendOnlyRepository.__dict__
