from __future__ import annotations

from collections.abc import Callable
from typing import Any

from strategies.base import Strategy


StrategyFactory = Callable[..., Strategy]


class StrategyRegistry:
    """Registry for named strategy factories."""

    def __init__(self) -> None:
        self._strategies: dict[str, StrategyFactory] = {}

    def register(
        self,
        strategy_id: str,
        factory: StrategyFactory,
    ) -> None:
        if not strategy_id:
            raise ValueError("strategy_id must not be empty")

        if strategy_id in self._strategies:
            raise ValueError(
                f"strategy already registered: {strategy_id}"
            )

        self._strategies[strategy_id] = factory

    def get(self, strategy_id: str) -> StrategyFactory:
        try:
            return self._strategies[strategy_id]
        except KeyError as exc:
            raise KeyError(
                f"unknown strategy: {strategy_id}"
            ) from exc

    def create(
        self,
        strategy_id: str,
        **kwargs: Any,
    ) -> Strategy:
        factory = self.get(strategy_id)
        return factory(**kwargs)

    def contains(self, strategy_id: str) -> bool:
        return strategy_id in self._strategies

    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._strategies))


def create_default_registry() -> StrategyRegistry:
    from strategies.ema_cross import EMACrossStrategy
    from strategies.trend_state import TrendStateStrategy

    registry = StrategyRegistry()

    registry.register(
        EMACrossStrategy.strategy_id,
        EMACrossStrategy,
    )

    registry.register(
        TrendStateStrategy.strategy_id,
        TrendStateStrategy,
    )

    return registry
