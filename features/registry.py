from __future__ import annotations

from collections.abc import Callable

import polars as pl


FeatureFunction = Callable[[pl.DataFrame], pl.DataFrame]


class FeatureRegistry:
    """Registry for reusable feature pipelines."""

    def __init__(self) -> None:
        self._features: dict[str, FeatureFunction] = {}

    def register(
        self,
        name: str,
        feature: FeatureFunction,
    ) -> None:
        if not name:
            raise ValueError("Feature name cannot be empty")

        if name in self._features:
            raise ValueError(f"Feature already registered: {name}")

        self._features[name] = feature

    def get(self, name: str) -> FeatureFunction:
        try:
            return self._features[name]
        except KeyError as exc:
            raise KeyError(f"Unknown feature: {name}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._features))

    def apply(
        self,
        bars: pl.DataFrame,
        names: list[str] | tuple[str, ...],
    ) -> pl.DataFrame:
        result = bars

        for name in names:
            result = self.get(name)(result)

        return result
