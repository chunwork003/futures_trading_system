from __future__ import annotations

from backtest.capital_drawdown import calculate_capital_drawdown
from backtest.fixed_ratio_capital_position_input import (
    FixedRatioCapitalPositionInput,
)
from backtest.fixed_ratio_protected_quantity import (
    calculate_protected_quantity,
)
from backtest.fixed_ratio_quantity import calculate_fixed_ratio_quantity
from backtest.fixed_ratio_parameters import FixedRatioParameters
from backtest.fixed_ratio_risk_level_calculator import (
    determine_fixed_ratio_risk_level,
)


class FixedRatioCapitalPositionStrategy:
    def __init__(
        self,
        parameters: FixedRatioParameters,
    ) -> None:
        self.parameters = parameters

    def calculate(
        self,
        sizing_input: FixedRatioCapitalPositionInput,
    ) -> int:
        drawdown = calculate_capital_drawdown(
            equity=sizing_input.equity,
            reference_equity=sizing_input.reference_equity,
        )

        risk_level = determine_fixed_ratio_risk_level(
            drawdown=drawdown,
            thresholds=sizing_input.risk_thresholds,
        )

        base_quantity = calculate_fixed_ratio_quantity(
            equity=sizing_input.equity,
            parameters=self.parameters.model_copy(
                update={
                    "base_quantity": sizing_input.base_quantity,
                }
            ),
        )

        return calculate_protected_quantity(
            base_quantity=base_quantity,
            level=risk_level,
            multipliers=sizing_input.risk_multipliers,
        )
