from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from analysis.drawdown import DrawdownAnalyzer
from analysis.equity import EquityCurve
from analysis.performance_metrics import (
    PerformanceMetrics,
    PerformanceMetricsAnalyzer,
)
from analysis.trade_statistics import (
    TradeStatistics,
    TradeStatisticsAnalyzer,
)
from backtest.models import Trade


@dataclass(frozen=True)
class PerformanceReport:
    """Unified performance report for a backtest."""

    trade_statistics: TradeStatistics
    performance_metrics: PerformanceMetrics
    final_equity: float | None
    max_drawdown: float
    max_drawdown_pct: float
    longest_drawdown_bars: int
    longest_recovery_bars: int | None

    @classmethod
    def from_trades(
        cls,
        trades: Iterable[Trade],
        equity_curve: EquityCurve | None = None,
    ) -> "PerformanceReport":
        trades = list(trades)

        trade_statistics = TradeStatisticsAnalyzer(trades).calculate()
        performance_metrics = PerformanceMetricsAnalyzer(trades).calculate()

        if equity_curve is None:
            final_equity = None
            max_drawdown = 0.0
            max_drawdown_pct = 0.0
            longest_drawdown_bars = 0
            longest_recovery_bars = None
        else:
            final_equity = equity_curve.final_equity
            drawdown = DrawdownAnalyzer(equity_curve)

            max_drawdown = drawdown.maximum_drawdown
            max_drawdown_pct = drawdown.maximum_drawdown_pct
            longest_drawdown_bars = drawdown.longest_drawdown_bars
            longest_recovery_bars = drawdown.longest_recovery_bars

        return cls(
            trade_statistics=trade_statistics,
            performance_metrics=performance_metrics,
            final_equity=final_equity,
            max_drawdown=max_drawdown,
            max_drawdown_pct=max_drawdown_pct,
            longest_drawdown_bars=longest_drawdown_bars,
            longest_recovery_bars=longest_recovery_bars,
        )
