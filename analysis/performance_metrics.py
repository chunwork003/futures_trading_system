from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from backtest.models import Trade


@dataclass(frozen=True)
class PerformanceMetrics:
    profit_factor: float
    expectancy: float
    expectancy_r: float | None


class PerformanceMetricsAnalyzer:
    """Calculate strategy-level performance metrics."""

    def __init__(self, trades: Iterable[Trade]) -> None:
        self.trades = list(trades)

    def calculate(self) -> PerformanceMetrics:
        if not self.trades:
            return PerformanceMetrics(
                profit_factor=0.0,
                expectancy=0.0,
                expectancy_r=None,
            )

        net_pnls = [float(trade.net_pnl) for trade in self.trades]

        gross_profit = sum(pnl for pnl in net_pnls if pnl > 0)
        gross_loss = abs(sum(pnl for pnl in net_pnls if pnl < 0))

        if gross_loss == 0:
            if gross_profit > 0:
                profit_factor = float("inf")
            else:
                profit_factor = 0.0
        else:
            profit_factor = gross_profit / gross_loss

        expectancy = sum(net_pnls) / len(net_pnls)

        r_values = [
            float(trade.r_multiple)
            for trade in self.trades
            if trade.r_multiple is not None
        ]

        expectancy_r = (
            sum(r_values) / len(r_values)
            if r_values
            else None
        )

        return PerformanceMetrics(
            profit_factor=profit_factor,
            expectancy=expectancy,
            expectancy_r=expectancy_r,
        )
