from __future__ import annotations

from math import floor

from pydantic import BaseModel, Field

from backtest.position_sizing import PositionSizingInput, PositionSizingStrategy


class StopBasedRiskSizing(PositionSizingStrategy, BaseModel):
    risk_amount: float = Field(gt=0)

    def calculate(self, sizing_input: PositionSizingInput) -> int:
        risk_per_contract = (
            abs(sizing_input.price - sizing_input.stop_price)
            * sizing_input.multiplier
        )

        if risk_per_contract <= 0:
            raise ValueError("stop distance must be greater than zero")

        return floor(self.risk_amount / risk_per_contract)
