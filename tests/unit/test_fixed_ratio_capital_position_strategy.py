from backtest.fixed_ratio_capital_position_input import (
    FixedRatioCapitalPositionInput,
)
from backtest.fixed_ratio_capital_position_strategy import (
    FixedRatioCapitalPositionStrategy,
)
from backtest.fixed_ratio_parameters import FixedRatioParameters
from backtest.fixed_ratio_risk_multipliers import FixedRatioRiskMultipliers
from backtest.fixed_ratio_risk_thresholds import FixedRatioRiskThresholds


def make_input(equity: float) -> FixedRatioCapitalPositionInput:
    return FixedRatioCapitalPositionInput(
        equity=equity,
        base_quantity=1,
        reference_equity=1_000_000,
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


def test_fixed_ratio_capital_position_strategy_normal():
    strategy = FixedRatioCapitalPositionStrategy(
        FixedRatioParameters(
            initial_equity=1_000_000,
            delta=100_000,
            base_quantity=1,
        )
    )

    assert strategy.calculate(make_input(1_200_000)) == 3


def test_fixed_ratio_capital_position_strategy_reduces_quantity_in_level_1():
    strategy = FixedRatioCapitalPositionStrategy(
        FixedRatioParameters(
            initial_equity=1_000_000,
            delta=100_000,
            base_quantity=1,
        )
    )

    assert strategy.calculate(make_input(950_000)) == 0


def test_fixed_ratio_capital_position_strategy_reduces_quantity_in_level_2():
    strategy = FixedRatioCapitalPositionStrategy(
        FixedRatioParameters(
            initial_equity=1_000_000,
            delta=100_000,
            base_quantity=1,
        )
    )

    assert strategy.calculate(make_input(900_000)) == 0


def test_fixed_ratio_capital_position_strategy_reduces_quantity_in_level_3():
    strategy = FixedRatioCapitalPositionStrategy(
        FixedRatioParameters(
            initial_equity=1_000_000,
            delta=100_000,
            base_quantity=1,
        )
    )

    assert strategy.calculate(make_input(800_000)) == 0
