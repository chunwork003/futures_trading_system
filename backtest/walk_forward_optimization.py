from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import polars as pl

from analysis.performance_report import PerformanceReport
from backtest.engine import BacktestConfig, BacktestEngine
from backtest.optimization import (
    DEFAULT_PARAMETER_GRID,
    OptimizationConstraint,
    OptimizationResult,
    TrendParameterOptimizer,
    TrendParameterSet,
)
from backtest.walk_forward import WalkForwardConfig, WalkForwardWindowGenerator
from features.trend import trend_features
from strategies.trend_state_exit import TrendStateExitStrategy


@dataclass(frozen=True)
class WalkForwardOptimizationConfig:
    window_config: WalkForwardConfig
    parameter_grid: tuple[TrendParameterSet, ...] = tuple(DEFAULT_PARAMETER_GRID)
    constraints: OptimizationConstraint = OptimizationConstraint()
    baseline: TrendParameterSet = TrendParameterSet(20, 60)


@dataclass(frozen=True)
class WalkForwardOptimizationResult:
    window_id: int

    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime

    selected_parameter_id: str
    selected_fast_window: int
    selected_slow_window: int

    train_trades: int
    train_expectancy: float
    train_profit_factor: float
    train_max_drawdown_pct: float
    train_net_profit: float

    oos_trades: int
    oos_expectancy: float
    oos_profit_factor: float
    oos_max_drawdown_pct: float
    oos_net_profit: float
    oos_final_equity: float


class WalkForwardOptimizer:
    def __init__(
        self,
        backtest_config: BacktestConfig,
        config: WalkForwardOptimizationConfig,
    ) -> None:
        self.backtest_config = backtest_config
        self.config = config

    def run(
        self,
        bars: pl.DataFrame,
    ) -> list[WalkForwardOptimizationResult]:
        if bars.is_empty():
            raise ValueError("bars must not be empty")

        timestamps = bars.get_column("timestamp").to_list()

        generator = WalkForwardWindowGenerator(
            self.config.window_config
        )

        windows = generator.generate(timestamps)

        results: list[WalkForwardOptimizationResult] = []

        for window in windows:
            train_df = bars.slice(
                window.train_start_index,
                window.train_size,
            )

            test_df = bars.slice(
                window.test_start_index,
                window.test_size,
            )

            train_results = self._optimize_train(train_df)
            selected = self._select_parameter(train_results)

            oos_report = self._evaluate_parameter(
                train_df=train_df,
                test_df=test_df,
                parameter=selected,
            )

            results.append(
                WalkForwardOptimizationResult(
                    window_id=window.window_id,
                    train_start=window.train_start,
                    train_end=window.train_end,
                    test_start=window.test_start,
                    test_end=window.test_end,
                    selected_parameter_id=selected.parameter_id,
                    selected_fast_window=selected.fast_window,
                    selected_slow_window=selected.slow_window,
                    train_trades=selected.total_trades,
                    train_expectancy=selected.expectancy,
                    train_profit_factor=selected.profit_factor,
                    train_max_drawdown_pct=selected.max_drawdown_pct,
                    train_net_profit=selected.net_profit,
                    oos_trades=oos_report.trade_statistics.total_trades,
                    oos_expectancy=oos_report.performance_metrics.expectancy,
                    oos_profit_factor=oos_report.performance_metrics.profit_factor,
                    oos_max_drawdown_pct=oos_report.max_drawdown_pct,
                    oos_net_profit=oos_report.trade_statistics.net_profit,
                    oos_final_equity=oos_report.final_equity,
                )
            )

        return results

    def _optimize_train(
        self,
        train_df: pl.DataFrame,
    ) -> list[OptimizationResult]:
        optimizer = TrendParameterOptimizer(
            backtest_config=self.backtest_config,
            parameter_grid=self.config.parameter_grid,
            baseline=self.config.baseline,
            constraints=self.config.constraints,
        )

        return optimizer.run(train_df)

    @staticmethod
    def _select_parameter(
        results: list[OptimizationResult],
    ) -> OptimizationResult:
        if not results:
            raise ValueError("optimization results must not be empty")

        return sorted(
            results,
            key=lambda result: (
                result.passes_constraints,
                result.expectancy,
                result.profit_factor,
            ),
            reverse=True,
        )[0]

    def _evaluate_parameter(
        self,
        train_df: pl.DataFrame,
        test_df: pl.DataFrame,
        parameter: OptimizationResult,
    ) -> PerformanceReport:
        combined = pl.concat(
            [
                train_df,
                test_df,
            ],
            how="vertical",
        )

        featured = trend_features(
            combined,
            fast_window=parameter.fast_window,
            slow_window=parameter.slow_window,
        )

        test_featured = featured.slice(
            train_df.height,
            test_df.height,
        )

        strategy = TrendStateExitStrategy(
            symbol=self.backtest_config.symbol
        )
        strategy.reset()

        signals = []

        for row in test_featured.iter_rows(named=True):
            signals.extend(strategy.on_bar(row))

        engine = BacktestEngine(self.backtest_config)

        trade_result = engine.run(
            bars=test_featured.iter_rows(named=True),
            signals=signals,
        )

        return PerformanceReport.from_trades(
            trade_result,
            equity_curve=engine.equity_curve,
        )
