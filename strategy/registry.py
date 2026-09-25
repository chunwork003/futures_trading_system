from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


StrategyFactory = Callable[..., Any]


@dataclass(frozen=True)
class StrategyDefinition:
    strategy_id: str
    version: str
    factory: StrategyFactory


class StrategyRegistry:
    def __init__(self) -> None:
        self._strategies: dict[str, StrategyDefinition] = {}

    def register(
        self,
        strategy_id: str,
        version: str,
        factory: StrategyFactory,
    ) -> None:
        if not strategy_id.strip():
            raise ValueError("strategy_id must not be empty")

        if not version.strip():
            raise ValueError("version must not be empty")

        if strategy_id in self._strategies:
            raise ValueError(
                f"strategy already registered: {strategy_id}"
            )

        self._strategies[strategy_id] = StrategyDefinition(
            strategy_id=strategy_id,
            version=version,
            factory=factory,
        )

    def get(self, strategy_id: str) -> StrategyDefinition:
        try:
            return self._strategies[strategy_id]
        except KeyError as exc:
            raise KeyError(
                f"strategy not registered: {strategy_id}"
            ) from exc

    def create(
        self,
        strategy_id: str,
        **kwargs: Any,
    ) -> Any:
        definition = self.get(strategy_id)
        return definition.factory(**kwargs)

    def create_instance(self, instance: "StrategyInstance") -> Any:
        """依 immutable StrategyInstance 建立 runtime，拒絕 version/config/scope drift。"""

        from strategy.instance import StrategyInstance

        if not isinstance(instance, StrategyInstance):
            raise TypeError("instance must be StrategyInstance")
        definition = self.get(instance.strategy_id)
        if definition.version != instance.strategy_version:
            raise ValueError("strategy version mismatch")
        config = dict(instance.config_json)
        config_instrument = config.pop("instrument_id", instance.instrument_id)
        config_timeframe = config.get("timeframe", instance.timeframe)
        if config_instrument != instance.instrument_id or config_timeframe != instance.timeframe:
            raise ValueError("strategy config scope mismatch")
        return definition.factory(**config)

    def contains(self, strategy_id: str) -> bool:
        return strategy_id in self._strategies

    def list(self) -> tuple[StrategyDefinition, ...]:
        return tuple(self._strategies.values())
