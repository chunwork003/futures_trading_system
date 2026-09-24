from __future__ import annotations

from pydantic import BaseModel, Field


class PositionSizingInput(BaseModel):
    equity: float = Field(gt=0)
    price: float = Field(gt=0)
    stop_price: float = Field(gt=0)
    multiplier: float = Field(gt=0)
    risk_budget: float = Field(gt=0, le=1)
