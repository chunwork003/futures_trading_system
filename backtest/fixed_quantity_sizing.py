from __future__ import annotations

from pydantic import BaseModel, Field

from backtest.position_sizing import PositionSizingInput, PositionSizingStrategy


class FixedQuantitySizing(PositionSizingStrategy, BaseModel):
    quantity: int = Field(gt=0)

    def calculate(self, sizing_input: PositionSizingInput) -> int:
        return self.quantity
