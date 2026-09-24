from datetime import datetime, timezone

import pytest

from trading.account import (
    AccountPosition,
    BrokerPositionSnapshot,
    PositionDirection,
)
from trading.reconciliation import (
    PositionComparisonError,
    ReconciliationStatus,
    compare_positions,
)


def _expected(**overrides: object) -> AccountPosition:
    values: dict[str, object] = {
        "broker": "SINOPAC",
        "account_ref": "9A95-1234567",
        "instrument_id": 1,
        "contract_id": 101,
        "direction": PositionDirection.LONG,
        "quantity": 2,
    }
    values.update(overrides)
    return AccountPosition(**values)


def _actual(**overrides: object) -> BrokerPositionSnapshot:
    values: dict[str, object] = {
        **_expected().model_dump(),
        "observed_at": datetime.now(timezone.utc),
    }
    values.update(overrides)
    return BrokerPositionSnapshot(**values)


@pytest.mark.parametrize(
    ("expected", "actual", "status"),
    [
        (None, None, ReconciliationStatus.MATCH),
        (_expected(), None, ReconciliationStatus.INTERNAL_ONLY),
        (None, _actual(), ReconciliationStatus.BROKER_ONLY),
        (_expected(), _actual(), ReconciliationStatus.MATCH),
        (
            _expected(),
            _actual(contract_id=102),
            ReconciliationStatus.CONTRACT_MISMATCH,
        ),
        (
            _expected(),
            _actual(direction=PositionDirection.SHORT),
            ReconciliationStatus.DIRECTION_MISMATCH,
        ),
        (
            _expected(),
            _actual(quantity=3),
            ReconciliationStatus.QUANTITY_MISMATCH,
        ),
    ],
)
def test_pairwise_reconciliation_statuses(
    expected: AccountPosition | None,
    actual: BrokerPositionSnapshot | None,
    status: ReconciliationStatus,
) -> None:
    result = compare_positions(expected, actual)

    assert result.status == status
    assert result.expected is expected
    assert result.actual is actual


@pytest.mark.parametrize(
    "actual",
    [
        _actual(broker="OTHER"),
        _actual(account_ref="OTHER-ACCOUNT"),
        _actual(instrument_id=2),
    ],
)
def test_non_comparable_identity_is_explicit(
    actual: BrokerPositionSnapshot,
) -> None:
    with pytest.raises(PositionComparisonError, match="do not share"):
        compare_positions(_expected(), actual)


def test_comparison_does_not_mutate_or_offer_corrective_execution() -> None:
    expected = _expected()
    actual = _actual(quantity=3)
    before_expected = expected.model_dump()
    before_actual = actual.model_dump()

    result = compare_positions(expected, actual)

    assert expected.model_dump() == before_expected
    assert actual.model_dump() == before_actual
    assert "submit" not in result.__class__.__dict__
    assert "repair" not in result.__class__.__dict__
