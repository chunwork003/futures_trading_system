from backtest.fixed_ratio_capital_position_input import (
    FixedRatioCapitalPositionInput,
)
from backtest.fixed_ratio_risk_multipliers import FixedRatioRiskMultipliers
from backtest.fixed_ratio_risk_thresholds import FixedRatioRiskThresholds


def test_fixed_ratio_capital_position_input_accepts_reference_equity():
    result = FixedRatioCapitalPositionInput(
        equity=1_200_000,
        base_quantity=3,
        reference_equity=1_100_000,
        risk_thresholds=FixedRatioRiskThresholds(
            level_1_drawdown=0.05,
            level_2_drawdown=0.10,
            level_3_drawdown=0.15,
        ),
        risk_multipliers=FixedRatioRiskMultipliers(
            normal=1.0,
            level_1=0.75,
            level_2=0.50,
            level_3=0.25,
        ),
    )

    assert result.reference_equity == 1_100_000
