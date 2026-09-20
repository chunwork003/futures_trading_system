from __future__ import annotations

from dataclasses import asdict, dataclass
from math import sqrt
from typing import Iterable

from backtest.optimization import OptimizationResult


@dataclass(frozen=True)
class StabilityConfig:
    neighbor_count: int = 3


@dataclass(frozen=True)
class ParameterStabilityResult:
    parameter_id: str
    fast_window: int
    slow_window: int

    neighbor_count: int
    neighbor_parameter_ids: tuple[str, ...]

    expectancy: float
    neighbor_expectancy_median: float
    expectancy_range: float

    profit_factor: float
    neighbor_profit_factor_median: float
    profit_factor_range: float

    max_drawdown_pct: float
    neighbor_max_drawdown_pct_median: float
    max_drawdown_range: float

    expectancy_delta_vs_neighbors: float
    profit_factor_delta_vs_neighbors: float
    max_drawdown_delta_vs_neighbors: float

    def to_dict(self) -> dict:
        return asdict(self)


class ParameterStabilityAnalyzer:
    def __init__(
        self,
        results: Iterable[OptimizationResult],
        config: StabilityConfig = StabilityConfig(),
    ) -> None:
        self.results = list(results)
        self.config = config

        if self.config.neighbor_count <= 0:
            raise ValueError("neighbor_count must be greater than zero")

        if not self.results:
            raise ValueError("results must not be empty")

    @staticmethod
    def _distance(
        left: OptimizationResult,
        right: OptimizationResult,
    ) -> float:
        return sqrt(
            (left.fast_window - right.fast_window) ** 2
            + (left.slow_window - right.slow_window) ** 2
        )

    def _neighbors(
        self,
        target: OptimizationResult,
    ) -> list[OptimizationResult]:
        candidates = [
            result
            for result in self.results
            if result.parameter_id != target.parameter_id
        ]

        candidates.sort(
            key=lambda result: (
                self._distance(target, result),
                result.parameter_id,
            )
        )

        return candidates[: self.config.neighbor_count]

    @staticmethod
    def _median(values: list[float]) -> float:
        ordered = sorted(values)
        size = len(ordered)

        if size == 0:
            raise ValueError("cannot calculate median of empty values")

        middle = size // 2

        if size % 2:
            return ordered[middle]

        return (ordered[middle - 1] + ordered[middle]) / 2.0

    @staticmethod
    def _range(values: list[float]) -> float:
        if not values:
            raise ValueError("cannot calculate range of empty values")

        return max(values) - min(values)

    def analyze_one(
        self,
        target: OptimizationResult,
    ) -> ParameterStabilityResult:
        neighbors = self._neighbors(target)

        if not neighbors:
            raise ValueError(
                f"no neighbors available for {target.parameter_id}"
            )

        expectancy_values = [
            result.expectancy for result in neighbors
        ]
        profit_factor_values = [
            result.profit_factor for result in neighbors
        ]
        drawdown_values = [
            result.max_drawdown_pct for result in neighbors
        ]

        neighbor_expectancy_median = self._median(expectancy_values)
        neighbor_profit_factor_median = self._median(profit_factor_values)
        neighbor_drawdown_median = self._median(drawdown_values)

        return ParameterStabilityResult(
            parameter_id=target.parameter_id,
            fast_window=target.fast_window,
            slow_window=target.slow_window,
            neighbor_count=len(neighbors),
            neighbor_parameter_ids=tuple(
                result.parameter_id for result in neighbors
            ),
            expectancy=target.expectancy,
            neighbor_expectancy_median=neighbor_expectancy_median,
            expectancy_range=self._range(expectancy_values),
            profit_factor=target.profit_factor,
            neighbor_profit_factor_median=neighbor_profit_factor_median,
            profit_factor_range=self._range(profit_factor_values),
            max_drawdown_pct=target.max_drawdown_pct,
            neighbor_max_drawdown_pct_median=neighbor_drawdown_median,
            max_drawdown_range=self._range(drawdown_values),
            expectancy_delta_vs_neighbors=(
                target.expectancy - neighbor_expectancy_median
            ),
            profit_factor_delta_vs_neighbors=(
                target.profit_factor - neighbor_profit_factor_median
            ),
            max_drawdown_delta_vs_neighbors=(
                target.max_drawdown_pct - neighbor_drawdown_median
            ),
        )

    def analyze(self) -> list[ParameterStabilityResult]:
        return [
            self.analyze_one(result)
            for result in self.results
        ]
