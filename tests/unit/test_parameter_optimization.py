from __future__ import annotations

import polars as pl
import pytest

from backtest.engine import BacktestConfig
from backtest.optimization import (
    DEFAULT_PARAMETER_GRID,
    OptimizationConstraint,
    TrendParameterOptimizer,
    TrendParameterSet,
)


def test_parameter_id() -> None:
    params = TrendParameterSet(20, 60)

    assert params.parameter_id == "ema_20_60"


def test_default_parameter_grid_contains_baseline() -> None:
    assert TrendParameterSet(20, 60) in DEFAULT_PARAMETER_GRID


def test_parameter_grid_has_valid_order() -> None:
    assert len(DEFAULT_PARAMETER_GRID) >= 5

    for params in DEFAULT_PARAMETER_GRID:
        assert params.fast_window > 0
        assert params.slow_window > 0
        assert params.fast_window < params.slow_window


def test_optimizer_rejects_invalid_parameter_order() -> None:
    optimizer = TrendParameterOptimizer(
        backtest_config=BacktestConfig(
            symbol="TXF",
        ),
        parameter_grid=[
            TrendParameterSet(60, 20),
        ],
    )

    bars = pl.DataFrame(
        {
            "timestamp": [],
            "open": [],
            "high": [],
            "low": [],
            "close": [],
            "volume": [],
        }
    )

    with pytest.raises(ValueError):
        optimizer.run(bars)


def test_constraint_defaults() -> None:
    constraint = OptimizationConstraint()

    assert constraint.min_trades == 100
    assert constraint.min_profit_factor == 1.0
    assert constraint.max_drawdown_pct == -80.0
