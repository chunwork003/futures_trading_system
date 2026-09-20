from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import polars as pl

from analysis.performance_report import PerformanceReport
from backtest.engine import BacktestConfig, BacktestEngine
from features.trend import trend_features
from strategies.trend_state_exit import TrendStateExitStrategy


@dataclass(frozen=True)
class TrendParameterSet:
    fast_window: int
    slow_window: int

    @property
    def parameter_id(self) -> str:
        return f"ema_{self.fast_window}_{self.slow_window}"


@dataclass(frozen=True)
class OptimizationConstraint:
    min_trades: int = 100
    min_profit_factor: float = 1.0
    max_drawdown_pct: float = -80.0


@dataclass(frozen=True)
class OptimizationResult:
    parameter_id: str
    fast_window: int
    slow_window: int
    total_trades: int
    win_rate: float
    net_profit: float
    average_trade: float
    profit_factor: float
    expectancy: float
    max_drawdown: float
    max_drawdown_pct: float
    final_equity: float
    is_baseline: bool
    passes_constraints: bool


DEFAULT_PARAMETER_GRID = [
    TrendParameterSet(5, 20),
    TrendParameterSet(10, 30),
    TrendParameterSet(10, 40),
    TrendParameterSet(15, 45),
    TrendParameterSet(15, 50),
    TrendParameterSet(20, 60),
    TrendParameterSet(20, 80),
    TrendParameterSet(25, 75),
    TrendParameterSet(30, 90),
    TrendParameterSet(40, 120),
]


class TrendParameterOptimizer:
    def __init__(
        self,
        backtest_config: BacktestConfig,
        parameter_grid: Iterable[TrendParameterSet] | None = None,
        baseline: TrendParameterSet = TrendParameterSet(20, 60),
        constraints: OptimizationConstraint = OptimizationConstraint(),
    ) -> None:
        self.backtest_config = backtest_config
        self.parameter_grid = list(parameter_grid or DEFAULT_PARAMETER_GRID)
        self.baseline = baseline
        self.constraints = constraints

    def run(self, bars: pl.DataFrame) -> list[OptimizationResult]:
        results: list[OptimizationResult] = []

        for params in self.parameter_grid:
            if params.fast_window >= params.slow_window:
                raise ValueError(
                    f"fast_window must be smaller than slow_window: "
                    f"{params.fast_window}/{params.slow_window}"
                )

            featured = trend_features(
                bars,
                fast_window=params.fast_window,
                slow_window=params.slow_window,
            )

            strategy = TrendStateExitStrategy(symbol=self.backtest_config.symbol)
            strategy.reset()

            signals = []
            for row in featured.iter_rows(named=True):
                signals.extend(strategy.on_bar(row))

            engine = BacktestEngine(self.backtest_config)
            result = engine.run(bars=featured.iter_rows(named=True), signals=signals)

            report = PerformanceReport.from_trades(
                result,
                equity_curve=engine.equity_curve,
            )

            stats = report.trade_statistics
            metrics = report.performance_metrics

            passes_constraints = (
                stats.total_trades >= self.constraints.min_trades
                and metrics.profit_factor >= self.constraints.min_profit_factor
                and report.max_drawdown_pct >= self.constraints.max_drawdown_pct
            )

            results.append(
                OptimizationResult(
                    parameter_id=params.parameter_id,
                    fast_window=params.fast_window,
                    slow_window=params.slow_window,
                    total_trades=stats.total_trades,
                    win_rate=stats.win_rate,
                    net_profit=stats.net_profit,
                    average_trade=stats.average_trade,
                    profit_factor=metrics.profit_factor,
                    expectancy=metrics.expectancy,
                    max_drawdown=report.max_drawdown,
                    max_drawdown_pct=report.max_drawdown_pct,
                    final_equity=report.final_equity,
                    is_baseline=params == self.baseline,
                    passes_constraints=passes_constraints,
                )
            )

        return results


