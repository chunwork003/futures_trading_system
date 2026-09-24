import pytest

from backtest.fixed_ratio_risk_thresholds import FixedRatioRiskThresholds


def test_fixed_ratio_risk_thresholds_accept_ordered_values():
    result = FixedRatioRiskThresholds(
        level_1_drawdown=0.05,
        level_2_drawdown=0.10,
        level_3_drawdown=0.15,
    )

    assert result.level_1_drawdown == 0.05
    assert result.level_2_drawdown == 0.10
    assert result.level_3_drawdown == 0.15


@pytest.mark.parametrize(
    ("level_1", "level_2", "level_3"),
    [
        (0.10, 0.05, 0.15),
        (0.05, 0.15, 0.10),
        (0.10, 0.10, 0.15),
        (0.05, 0.10, 0.10),
    ],
)
def test_fixed_ratio_risk_thresholds_reject_invalid_order(
    level_1: float,
    level_2: float,
    level_3: float,
):
    with pytest.raises(ValueError):
        FixedRatioRiskThresholds(
            level_1_drawdown=level_1,
            level_2_drawdown=level_2,
            level_3_drawdown=level_3,
        )
