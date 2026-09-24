from __future__ import annotations

from math import floor

from backtest.fixed_ratio_parameters import FixedRatioParameters


def calculate_fixed_ratio_quantity(
    equity: float,
    parameters: FixedRatioParameters,
) -> int:
    if equity <= 0:
        raise ValueError("equity must be greater than zero")

    accumulated_profit = max(
        0,
        equity - parameters.initial_equity,
    )

    profit_steps = floor(
        accumulated_profit / parameters.delta,
    )

    return parameters.base_quantity + profit_steps
