from __future__ import annotations

from typing import Any, Iterable

from backtest.engine import BacktestEngine
from backtest.models import BacktestConfig
from analysis.performance_report import PerformanceReport
from strategy.multi_runner import MultiStrategyRunner


class MultiStrategyBacktestResult:
    def __init__(
        self,
        strategy_id: str,
        version: str,
        signal_count: int,
        report: PerformanceReport,
    ) -> None:
        self.strategy_id = strategy_id
        self.version = version
        self.signal_count = signal_count
        self.report = report


class MultiStrategyBacktestRunner:
    def __init__(
        self,
        strategy_runner: MultiStrategyRunner,
    ) -> None:
        self.strategy_runner = strategy_runner

    def run(
        self,
        strategy_ids: Iterable[str],
        bars: list[dict[str, Any]],
        backtest_config: BacktestConfig,
        **strategy_kwargs: Any,
    ) -> list[MultiStrategyBacktestResult]:
        strategy_results = self.strategy_runner.run(
            strategy_ids=strategy_ids,
            bars=bars,
            **strategy_kwargs,
        )

        results: list[MultiStrategyBacktestResult] = []

        for strategy_result in strategy_results:
            engine = BacktestEngine(backtest_config)

            trades = engine.run(
                bars=bars,
                signals=strategy_result.signals,
            )

            report = PerformanceReport.from_trades(
                trades,
                engine.equity_curve,
            )

            results.append(
                MultiStrategyBacktestResult(
                    strategy_id=strategy_result.strategy_id,
                    version=strategy_result.version,
                    signal_count=len(strategy_result.signals),
                    report=report,
                )
            )

        return results


