from __future__ import annotations

import pytest

from backtest.optimization import OptimizationResult
from backtest.parameter_stability import (
    ParameterStabilityAnalyzer,
    StabilityConfig,
)


def make_result(
    parameter_id: str,
    fast_window: int,
    slow_window: int,
    expectancy: float,
    profit_factor: float,
    max_drawdown_pct: float,
) -> OptimizationResult:
    return OptimizationResult(
        parameter_id=parameter_id,
        fast_window=fast_window,
        slow_window=slow_window,
        total_trades=1000,
        win_rate=0.30,
        net_profit=100000.0,
        average_trade=expectancy,
        profit_factor=profit_factor,
        expectancy=expectancy,
        max_drawdown=-500000.0,
        max_drawdown_pct=max_drawdown_pct,
        final_equity=1100000.0,
        is_baseline=False,
        passes_constraints=True,
    )


@pytest.fixture
def results() -> list[OptimizationResult]:
    return [
        make_result("ema_15_50", 15, 50, 83.43, 1.0271, -0.4907),
        make_result("ema_10_40", 10, 40, 73.16, 1.0259, -0.4989),
        make_result("ema_20_60", 20, 60, 81.96, 1.0251, -0.5115),
        make_result("ema_15_45", 15, 45, 66.98, 1.0217, -0.5246),
    ]


def test_neighbor_selection_excludes_target(
    results: list[OptimizationResult],
) -> None:
    analyzer = ParameterStabilityAnalyzer(
        results,
        StabilityConfig(neighbor_count=2),
    )

    target = results[0]
    stability = analyzer.analyze_one(target)

    assert stability.parameter_id == "ema_15_50"
    assert stability.neighbor_count == 2
    assert stability.parameter_id not in stability.neighbor_parameter_ids


def test_neighbor_statistics_are_calculated(
    results: list[OptimizationResult],
) -> None:
    analyzer = ParameterStabilityAnalyzer(
        results,
        StabilityConfig(neighbor_count=3),
    )

    stability = analyzer.analyze_one(results[0])

    assert stability.neighbor_count == 3
    assert stability.neighbor_expectancy_median == pytest.approx(73.16)
    assert stability.neighbor_profit_factor_median == pytest.approx(1.0251)
    assert stability.expectancy_range == pytest.approx(14.98)
    assert stability.profit_factor_range == pytest.approx(0.0042)


def test_analyze_returns_all_parameter_results(
    results: list[OptimizationResult],
) -> None:
    analyzer = ParameterStabilityAnalyzer(results)

    output = analyzer.analyze()

    assert len(output) == len(results)
    assert {
        item.parameter_id for item in output
    } == {
        item.parameter_id for item in results
    }


def test_empty_results_are_rejected() -> None:
    with pytest.raises(ValueError, match="results must not be empty"):
        ParameterStabilityAnalyzer([])


def test_invalid_neighbor_count_is_rejected(
    results: list[OptimizationResult],
) -> None:
    with pytest.raises(
        ValueError,
        match="neighbor_count must be greater than zero",
    ):
        ParameterStabilityAnalyzer(
            results,
            StabilityConfig(neighbor_count=0),
        )
