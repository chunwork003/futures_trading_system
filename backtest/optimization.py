from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import polars as pl

from analysis.performance_report import PerformanceReport
from backtest.engine import BacktestEngine
from backtest.models import BacktestConfig
from features.trend import trend_features
from strategies.trend_state_exit import TrendStateExitStrategy


@dataclass(frozen=True)
class TrendParameterSet:
    fast_window: int
    slow_window: int

    @property
    def parameter_id(self) -> str:
        return f"ema_{self.fast_window}_{self.slow_window}"


@dataclass
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

    is_baseline: bool = False


DEFAULT_PARAMETER_GRID = [
    TrendParameterSet(10, 40),
    TrendParameterSet(15, 50),
    TrendParameterSet(20, 60),
    TrendParameterSet(20, 80),
    TrendParameterSet(25, 75),
    TrendParameterSet(30, 90),
]


class TrendParameterOptimizer:
    def __init__(
        self,
        *,
        symbol: str = "TXF",
        timeframe: str = "1m",
        initial_capital: float = 1_000_000.0,
        quantity: int = 1,
        multiplier: float = 200.0,
    ) -> None:
        self.symbol = symbol
        self.timeframe = timeframe
        self.initial_capital = initial_capital
        self.quantity = quantity
        self.multiplier = multiplier

    def run(
        self,
        bars: pl.DataFrame,
        parameters: Iterable[TrendParameterSet],
    ) -> list[OptimizationResult]:
        results: list[OptimizationResult] = []

        for parameter in parameters:
            features = trend_features(
                bars,
                fast_window=parameter.fast_window,
                slow_window=parameter.slow_window,
            )

            signals = self._generate_signals(features)

            config = BacktestConfig(
                initial_capital=self.initial_capital,
                symbol=self.symbol,
                timeframe=self.timeframe,
                quantity=self.quantity,
                multiplier=self.multiplier,
                commission_per_contract=0.0,
                slippage_points=0.0,
                allow_multiple_positions=False,
                intrabar_priority="SL_FIRST",
                end_of_data_exit=True,
            )

            engine = BacktestEngine(config)

            trades = engine.run(
                bars=features.iter_rows(named=True),
                signals=signals,
            )

            report = PerformanceReport.from_trades(
                trades,
                engine.equity_curve,
            )

            statistics = report.trade_statistics
            metrics = report.performance_metrics

            results.append(
                OptimizationResult(
                    parameter_id=parameter.parameter_id,
                    fast_window=parameter.fast_window,
                    slow_window=parameter.slow_window,
                    total_trades=statistics.total_trades,
                    win_rate=statistics.win_rate,
                    net_profit=statistics.net_profit,
                    average_trade=statistics.average_trade,
                    profit_factor=metrics.profit_factor,
                    expectancy=metrics.expectancy,
                    max_drawdown=report.max_drawdown,
                    max_drawdown_pct=report.max_drawdown_pct,
                    final_equity=report.final_equity,
                    is_baseline=(
                        parameter.fast_window == 20
                        and parameter.slow_window == 60
                    ),
                )
            )

        return results

    def _generate_signals(
        self,
        df: pl.DataFrame,
    ) -> list:
        strategy = TrendStateExitStrategy(
            symbol=self.symbol,
            timeframe=self.timeframe,
            quantity=self.quantity,
        )

        strategy.reset()

        signals = []

        for row in df.iter_rows(named=True):
            signals.extend(strategy.on_bar(row))

        return signals
