from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from statistics import median

from backtest.walk_forward_optimization import WalkForwardOptimizationResult


@dataclass(frozen=True)
class OOSWindowSummary:
    window_id: int
    test_start: datetime
    test_end: datetime
    parameter_id: str
    trades: int
    expectancy: float
    profit_factor: float
    max_drawdown_pct: float
    net_profit: float
    final_equity: float


@dataclass(frozen=True)
class OOSParameterFrequency:
    parameter_id: str
    selected_windows: int


@dataclass(frozen=True)
class OOSReport:
    window_count: int
    total_trades: int
    total_net_profit: float

    positive_windows: int
    negative_windows: int
    non_negative_window_ratio: float

    average_window_expectancy: float
    median_window_expectancy: float
    average_window_profit_factor: float
    median_window_profit_factor: float

    worst_window_net_profit: float
    best_window_net_profit: float
    worst_window_drawdown_pct: float

    selected_parameter_count: int
    parameter_frequencies: tuple[OOSParameterFrequency, ...]

    windows: tuple[OOSWindowSummary, ...]

    @property
    def oos_consistency_ratio(self) -> float:
        if self.window_count == 0:
            return 0.0

        return self.positive_windows / self.window_count

    def to_dict(self) -> dict:
        return {
            "window_count": self.window_count,
            "total_trades": self.total_trades,
            "total_net_profit": self.total_net_profit,
            "positive_windows": self.positive_windows,
            "negative_windows": self.negative_windows,
            "non_negative_window_ratio": self.non_negative_window_ratio,
            "average_window_expectancy": self.average_window_expectancy,
            "median_window_expectancy": self.median_window_expectancy,
            "average_window_profit_factor": self.average_window_profit_factor,
            "median_window_profit_factor": self.median_window_profit_factor,
            "worst_window_net_profit": self.worst_window_net_profit,
            "best_window_net_profit": self.best_window_net_profit,
            "worst_window_drawdown_pct": self.worst_window_drawdown_pct,
            "selected_parameter_count": self.selected_parameter_count,
            "parameter_frequencies": [
                {
                    "parameter_id": item.parameter_id,
                    "selected_windows": item.selected_windows,
                }
                for item in self.parameter_frequencies
            ],
            "windows": [
                {
                    "window_id": item.window_id,
                    "test_start": item.test_start.isoformat(),
                    "test_end": item.test_end.isoformat(),
                    "parameter_id": item.parameter_id,
                    "trades": item.trades,
                    "expectancy": item.expectancy,
                    "profit_factor": item.profit_factor,
                    "max_drawdown_pct": item.max_drawdown_pct,
                    "net_profit": item.net_profit,
                    "final_equity": item.final_equity,
                }
                for item in self.windows
            ],
        }


class OOSAggregator:
    def aggregate(
        self,
        results: list[WalkForwardOptimizationResult],
    ) -> OOSReport:
        if not results:
            raise ValueError("results must not be empty")

        windows = tuple(
            OOSWindowSummary(
                window_id=result.window_id,
                test_start=result.test_start,
                test_end=result.test_end,
                parameter_id=result.selected_parameter_id,
                trades=result.oos_trades,
                expectancy=result.oos_expectancy,
                profit_factor=result.oos_profit_factor,
                max_drawdown_pct=result.oos_max_drawdown_pct,
                net_profit=result.oos_net_profit,
                final_equity=result.oos_final_equity,
            )
            for result in results
        )

        total_trades = sum(item.trades for item in windows)
        total_net_profit = sum(item.net_profit for item in windows)

        positive_windows = sum(
            1 for item in windows if item.net_profit > 0
        )
        negative_windows = sum(
            1 for item in windows if item.net_profit < 0
        )

        expectancies = [item.expectancy for item in windows]
        profit_factors = [item.profit_factor for item in windows]

        parameter_counts: dict[str, int] = {}

        for item in windows:
            parameter_counts[item.parameter_id] = (
                parameter_counts.get(item.parameter_id, 0) + 1
            )

        parameter_frequencies = tuple(
            OOSParameterFrequency(
                parameter_id=parameter_id,
                selected_windows=count,
            )
            for parameter_id, count in sorted(
                parameter_counts.items(),
                key=lambda item: (-item[1], item[0]),
            )
        )

        return OOSReport(
            window_count=len(windows),
            total_trades=total_trades,
            total_net_profit=total_net_profit,
            positive_windows=positive_windows,
            negative_windows=negative_windows,
            non_negative_window_ratio=(
                sum(1 for item in windows if item.net_profit >= 0)
                / len(windows)
            ),
            average_window_expectancy=sum(expectancies)
            / len(expectancies),
            median_window_expectancy=median(expectancies),
            average_window_profit_factor=sum(profit_factors)
            / len(profit_factors),
            median_window_profit_factor=median(profit_factors),
            worst_window_net_profit=min(
                item.net_profit for item in windows
            ),
            best_window_net_profit=max(
                item.net_profit for item in windows
            ),
            worst_window_drawdown_pct=min(
                item.max_drawdown_pct for item in windows
            ),
            selected_parameter_count=len(parameter_frequencies),
            parameter_frequencies=parameter_frequencies,
            windows=windows,
        )


def aggregate_oos_results(
    results: list[WalkForwardOptimizationResult],
) -> OOSReport:
    return OOSAggregator().aggregate(results)
