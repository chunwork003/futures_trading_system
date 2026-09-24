from __future__ import annotations

from math import floor

from pydantic import BaseModel, Field

from backtest.position_sizing import PositionSizingInput, PositionSizingStrategy


class FixedAmountSizing(PositionSizingStrategy, BaseModel):
    amount: float = Field(gt=0)

    def calculate(self, sizing_input: PositionSizingInput) -> int:
        contract_value = sizing_input.price * sizing_input.multiplier
        return floor(self.amount / contract_value)
