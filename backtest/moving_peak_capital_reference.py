from __future__ import annotations

from backtest.capital_reference_strategy import CapitalReferenceStrategy


class MovingPeakCapitalReference(CapitalReferenceStrategy):
    def __init__(self, initial_equity: float) -> None:
        if initial_equity <= 0:
            raise ValueError("initial_equity must be greater than zero")

        self.peak_equity = initial_equity

    def update(self, equity: float) -> float:
        if equity <= 0:
            raise ValueError("equity must be greater than zero")

        self.peak_equity = max(self.peak_equity, equity)

        return self.peak_equity
