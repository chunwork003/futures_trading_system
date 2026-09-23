from __future__ import annotations

from pydantic import BaseModel, Field

from backtest.decision import DecisionAction
from backtest.models import Direction


class NettingResult(BaseModel):
    action: DecisionAction
    direction: Direction | None = None
    quantity: int = Field(gt=0)
