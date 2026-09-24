from __future__ import annotations

from backtest.position_sizing import PositionSizingStrategy


class PositionSizingRegistry:
    def __init__(self) -> None:
        self._strategies: dict[str, PositionSizingStrategy] = {}

    def register(
        self,
        name: str,
        strategy: PositionSizingStrategy,
    ) -> None:
        if not name:
            raise ValueError("strategy name must not be empty")

        if name in self._strategies:
            raise ValueError(
                f"position sizing strategy already registered: {name}"
            )

        self._strategies[name] = strategy

    def get(self, name: str) -> PositionSizingStrategy:
        try:
            return self._strategies[name]
        except KeyError as exc:
            raise KeyError(
                f"position sizing strategy not found: {name}"
            ) from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._strategies.keys())
