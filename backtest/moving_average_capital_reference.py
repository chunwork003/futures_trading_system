from __future__ import annotations

from collections import deque
from statistics import fmean

from pydantic import BaseModel, Field

from backtest.capital_reference_strategy import CapitalReferenceStrategy


class MovingAverageCapitalReference(
    CapitalReferenceStrategy,
    BaseModel,
):
    window: int = Field(gt=0)

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self._equity_history = deque(maxlen=self.window)

    def update(self, equity: float) -> float:
        if equity <= 0:
            raise ValueError("equity must be greater than zero")

        self._equity_history.append(equity)

        return fmean(self._equity_history)
