from __future__ import annotations

from backtest.capital_position_management_strategy import (
    CapitalPositionManagementStrategy,
)


class CapitalPositionManagementRegistry:
    def __init__(self) -> None:
        self._strategies: dict[
            str,
            CapitalPositionManagementStrategy,
        ] = {}

    def register(
        self,
        name: str,
        strategy: CapitalPositionManagementStrategy,
    ) -> None:
        if not name:
            raise ValueError("strategy name must not be empty")

        if name in self._strategies:
            raise ValueError(
                f"capital position management strategy already registered: {name}"
            )

        self._strategies[name] = strategy

    def get(
        self,
        name: str,
    ) -> CapitalPositionManagementStrategy:
        try:
            return self._strategies[name]
        except KeyError as exc:
            raise KeyError(
                f"capital position management strategy not found: {name}"
            ) from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._strategies.keys())
