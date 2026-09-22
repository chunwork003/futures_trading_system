from __future__ import annotations

from datetime import datetime

from backtest.models import BacktestConfig
from backtest.multi_strategy import MultiStrategyBacktestRunner
from strategy.multi_runner import MultiStrategyRunner
from strategy.registry import StrategyRegistry


class DummyStrategy:
    def __init__(self, strategy_id: str) -> None:
        self.strategy_id = strategy_id

    def generate_signals(self, bars):
        return []


def test_multi_strategy_backtest_runs_each_strategy_independently() -> None:
    registry = StrategyRegistry()

    registry.register(
        strategy_id="S1",
        version="1.0.0",
        factory=lambda: DummyStrategy("S1"),
    )
    registry.register(
        strategy_id="S2",
        version="1.0.0",
        factory=lambda: DummyStrategy("S2"),
    )

    runner = MultiStrategyBacktestRunner(
        MultiStrategyRunner(registry)
    )

    config = BacktestConfig(
        symbol="TXF",
        initial_capital=1_000_000,
        quantity=1,
        multiplier=200,
    )

    results = runner.run(
        strategy_ids=["S1", "S2"],
        bars=[
            {
                "timestamp": datetime(2026, 1, 2, 9, 0),
                "open": 100.0,
                "high": 101.0,
                "low": 99.0,
                "close": 100.0,
            }
        ],
        backtest_config=config,
    )

    assert len(results) == 2
    assert results[0].strategy_id == "S1"
    assert results[1].strategy_id == "S2"
    assert results[0].signal_count == 0
    assert results[1].signal_count == 0
    assert results[0].report.trade_statistics.total_trades == 0
    assert results[1].report.trade_statistics.total_trades == 0
