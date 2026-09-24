from __future__ import annotations

from math import floor

from backtest.position_sizing import PositionSizingInput, PositionSizingStrategy


class FixedRiskSizing(PositionSizingStrategy):
    def calculate(self, sizing_input: PositionSizingInput) -> int:
        risk_amount = sizing_input.equity * sizing_input.risk_budget
        risk_per_contract = (
            abs(sizing_input.price - sizing_input.stop_price)
            * sizing_input.multiplier
        )

        if risk_per_contract <= 0:
            raise ValueError("stop distance must be greater than zero")

        return floor(risk_amount / risk_per_contract)
