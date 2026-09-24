import pytest

from backtest.fixed_ratio_risk_level import FixedRatioRiskLevel
from backtest.fixed_ratio_risk_multiplier import get_risk_multiplier
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
        (FixedRatioRiskLevel.NORMAL, 1.0),
        (FixedRatioRiskLevel.LEVEL_1, 0.75),
        (FixedRatioRiskLevel.LEVEL_2, 0.50),
        (FixedRatioRiskLevel.LEVEL_3, 0.25),
    ],
)
def test_get_risk_multiplier(level, expected, multipliers):
    assert get_risk_multiplier(level, multipliers) == expected
