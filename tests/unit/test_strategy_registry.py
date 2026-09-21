from __future__ import annotations

import pytest

from strategy.registry import StrategyRegistry


class DummyStrategy:
    def __init__(self, value: int = 1) -> None:
        self.value = value

    def generate_signals(self, bars):
        return []


def test_register_and_get_strategy() -> None:
    registry = StrategyRegistry()

    registry.register(
        strategy_id="DUMMY",
        version="1.0.0",
        factory=DummyStrategy,
    )

    definition = registry.get("DUMMY")

    assert definition.strategy_id == "DUMMY"
    assert definition.version == "1.0.0"
    assert definition.factory is DummyStrategy


def test_create_strategy() -> None:
    registry = StrategyRegistry()

    registry.register(
        strategy_id="DUMMY",
        version="1.0.0",
        factory=DummyStrategy,
    )

    strategy = registry.create("DUMMY", value=5)

    assert isinstance(strategy, DummyStrategy)
    assert strategy.value == 5


def test_duplicate_strategy_is_rejected() -> None:
    registry = StrategyRegistry()

    registry.register(
        strategy_id="DUMMY",
        version="1.0.0",
        factory=DummyStrategy,
    )

    with pytest.raises(ValueError, match="already registered"):
        registry.register(
            strategy_id="DUMMY",
            version="2.0.0",
            factory=DummyStrategy,
        )


def test_unknown_strategy_is_rejected() -> None:
    registry = StrategyRegistry()

    with pytest.raises(KeyError, match="not registered"):
        registry.get("UNKNOWN")
