import pytest

from backtest.capital_position_management_strategy import (
    CapitalPositionManagementStrategy,
)
from backtest.fixed_ratio_capital_position_input import (
    FixedRatioCapitalPositionInput,
)


class DummyCapitalPositionManagementStrategy(
    CapitalPositionManagementStrategy
):
    def calculate(
        self,
        sizing_input: FixedRatioCapitalPositionInput,
    ) -> int:
        return sizing_input.base_quantity


def test_capital_position_management_strategy_defines_contract():
    strategy = DummyCapitalPositionManagementStrategy()

    assert strategy.calculate(
        FixedRatioCapitalPositionInput(
            equity=1_200_000,
            base_quantity=3,
            reference_equity=1_200_000,
            risk_thresholds={
                "level_1_drawdown": 0.05,
                "level_2_drawdown": 0.10,
                "level_3_drawdown": 0.15,
            },
            risk_multipliers={
                "normal": 1.0,
                "level_1": 0.75,
                "level_2": 0.50,
                "level_3": 0.25,
            },
        )
    ) == 3
