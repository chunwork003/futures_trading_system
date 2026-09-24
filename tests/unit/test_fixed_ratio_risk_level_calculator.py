import pytest

from backtest.fixed_ratio_risk_level import FixedRatioRiskLevel
from backtest.fixed_ratio_risk_level_calculator import (
    determine_fixed_ratio_risk_level,
)
from backtest.fixed_ratio_risk_thresholds import FixedRatioRiskThresholds


@pytest.fixture
def thresholds():
    return FixedRatioRiskThresholds(
        level_1_drawdown=0.05,
        level_2_drawdown=0.10,
        level_3_drawdown=0.15,
    )


@pytest.mark.parametrize(
    ("drawdown", "expected"),
    [
        (0.00, FixedRatioRiskLevel.NORMAL),
        (0.0499, FixedRatioRiskLevel.NORMAL),
        (0.05, FixedRatioRiskLevel.LEVEL_1),
        (0.0999, FixedRatioRiskLevel.LEVEL_1),
        (0.10, FixedRatioRiskLevel.LEVEL_2),
        (0.1499, FixedRatioRiskLevel.LEVEL_2),
        (0.15, FixedRatioRiskLevel.LEVEL_3),
        (0.25, FixedRatioRiskLevel.LEVEL_3),
    ],
)
def test_determine_fixed_ratio_risk_level(
    drawdown,
    expected,
    thresholds,
):
    assert (
        determine_fixed_ratio_risk_level(
            drawdown,
            thresholds,
        )
        == expected
    )


def test_negative_drawdown_is_rejected(thresholds):
    with pytest.raises(ValueError):
        determine_fixed_ratio_risk_level(-0.01, thresholds)
