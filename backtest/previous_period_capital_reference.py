from __future__ import annotations

from collections import deque

from pydantic import BaseModel, Field

from backtest.capital_reference_strategy import CapitalReferenceStrategy


class PreviousPeriodCapitalReference(
    CapitalReferenceStrategy,
    BaseModel,
):
    days: int = Field(gt=0)

    def __init__(self, **data) -> None:
        super().__init__(**data)
        self._equity_history = deque(maxlen=self.days)

    def update(self, equity: float) -> float:
        if equity <= 0:
            raise ValueError("equity must be greater than zero")

        if len(self._equity_history) < self.days:
            self._equity_history.append(equity)
            return equity

        reference_equity = self._equity_history[0]
        self._equity_history.append(equity)

        return reference_equity
