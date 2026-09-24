import pytest

from backtest.fixed_ratio_risk_thresholds import FixedRatioRiskThresholds


def test_fixed_ratio_risk_thresholds_accept_valid_values():
    thresholds = FixedRatioRiskThresholds(
        level_1_drawdown=0.05,
        level_2_drawdown=0.10,
        level_3_drawdown=0.15,
    )

    assert thresholds.level_1_drawdown == 0.05
    assert thresholds.level_2_drawdown == 0.10
    assert thresholds.level_3_drawdown == 0.15


@pytest.mark.parametrize(
    "field",
    [
        "level_1_drawdown",
        "level_2_drawdown",
        "level_3_drawdown",
    ],
)
def test_fixed_ratio_risk_thresholds_reject_non_positive_values(field):
    values = {
        "level_1_drawdown": 0.05,
        "level_2_drawdown": 0.10,
        "level_3_drawdown": 0.15,
    }
    values[field] = 0

    with pytest.raises(ValueError):
        FixedRatioRiskThresholds(**values)
