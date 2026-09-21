from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from strategy.multi_runner import MultiStrategyRunner
from strategy.registry import StrategyRegistry


class DummySignal(BaseModel):
    timestamp: datetime
    signal_id: str
    strategy_id: str


class DummyStrategy:
    def __init__(self, strategy_id: str) -> None:
        self.strategy_id = strategy_id

    def generate_signals(self, bars):
        return [
            DummySignal(
                timestamp=datetime(2026, 1, 2, 9, 1),
                signal_id=f"{self.strategy_id}-1",
                strategy_id=self.strategy_id,
            )
        ]


def test_multi_strategy_runner_returns_independent_results() -> None:
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

    runner = MultiStrategyRunner(registry)

    results = runner.run(
        strategy_ids=["S1", "S2"],
        bars=[],
    )

    assert len(results) == 2
    assert results[0].strategy_id == "S1"
    assert results[1].strategy_id == "S2"
    assert len(results[0].signals) == 1
    assert len(results[1].signals) == 1


def test_combined_signals_are_sorted() -> None:
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

    runner = MultiStrategyRunner(registry)

    signals = runner.run_combined(
        strategy_ids=["S2", "S1"],
        bars=[],
    )

    assert len(signals) == 2
    assert signals[0].strategy_id == "S1"
    assert signals[1].strategy_id == "S2"
