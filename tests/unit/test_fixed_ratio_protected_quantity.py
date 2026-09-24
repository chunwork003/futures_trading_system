import pytest

from backtest.fixed_ratio_protected_quantity import (
    calculate_protected_quantity,
)
from backtest.fixed_ratio_risk_level import FixedRatioRiskLevel
from backtest.fixed_ratio_risk_multipliers import FixedRatioRiskMultipliers


@pytest.fixture
def multipliers():
    return FixedRatioRiskMultipliers(
        normal=1.0,
        level_1=0.75,
        level_2=0.50,
        level_3=0.25,
    )


@pytest.mark.parametrize(
    ("level", "expected"),
    [
        (FixedRatioRiskLevel.NORMAL, 10),
        (FixedRatioRiskLevel.LEVEL_1, 7),
        (FixedRatioRiskLevel.LEVEL_2, 5),
        (FixedRatioRiskLevel.LEVEL_3, 2),
    ],
)
def test_calculate_protected_quantity(
    level,
    expected,
    multipliers,
):
    assert (
        calculate_protected_quantity(
            base_quantity=10,
            level=level,
            multipliers=multipliers,
        )
        == expected
    )


def test_protected_quantity_can_be_zero(multipliers):
    assert (
        calculate_protected_quantity(
            base_quantity=1,
            level=FixedRatioRiskLevel.LEVEL_3,
            multipliers=multipliers,
        )
        == 0
    )


def test_negative_base_quantity_is_rejected(multipliers):
    with pytest.raises(ValueError):
        calculate_protected_quantity(
            base_quantity=-1,
            level=FixedRatioRiskLevel.NORMAL,
            multipliers=multipliers,
        )
