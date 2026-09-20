from datetime import datetime, timedelta

import polars as pl
import pytest

from backtest.engine import BacktestConfig
from backtest.optimization import (
    OptimizationResult,
)
from backtest.walk_forward import WalkForwardConfig
from backtest.walk_forward_optimization import (
    WalkForwardOptimizationConfig,
    WalkForwardOptimizer,
)


def make_timestamps(count: int) -> list[datetime]:
    start = datetime(2026, 1, 1)

    return [
        start + timedelta(minutes=index)
        for index in range(count)
    ]


def make_bars(count: int = 100) -> pl.DataFrame:
    timestamps = make_timestamps(count)

    return pl.DataFrame(
        {
            "timestamp": timestamps,
            "trade_date": [
                timestamp.date()
                for timestamp in timestamps
            ],
            "open": [100.0] * count,
            "high": [101.0] * count,
            "low": [99.0] * count,
            "close": [100.0] * count,
            "volume": [1] * count,
        }
    )


def make_optimizer() -> WalkForwardOptimizer:
    backtest_config = BacktestConfig(
        symbol="TXF",
        initial_capital=1_000_000,
        quantity=1,
        multiplier=200,
    )

    config = WalkForwardOptimizationConfig(
        window_config=WalkForwardConfig(
            train_size=20,
            test_size=10,
            step_size=10,
        )
    )

    return WalkForwardOptimizer(
        backtest_config=backtest_config,
        config=config,
    )


def test_select_parameter_prefers_constraint_pass() -> None:
    results = [
        OptimizationResult(
            parameter_id="bad",
            fast_window=5,
            slow_window=20,
            total_trades=100,
            win_rate=0.30,
            net_profit=1000,
            average_trade=10,
            profit_factor=0.90,
            expectancy=500,
            max_drawdown=-100000,
            max_drawdown_pct=-0.50,
            final_equity=1_001_000,
            is_baseline=False,
            passes_constraints=False,
        ),
        OptimizationResult(
            parameter_id="good",
            fast_window=10,
            slow_window=40,
            total_trades=100,
            win_rate=0.30,
            net_profit=800,
            average_trade=8,
            profit_factor=1.01,
            expectancy=80,
            max_drawdown=-50000,
            max_drawdown_pct=-0.20,
            final_equity=1_000_800,
            is_baseline=False,
            passes_constraints=True,
        ),
    ]

    selected = make_optimizer()._select_parameter(results)

    assert selected.parameter_id == "good"


def test_select_parameter_prefers_expectancy_after_constraints() -> None:
    results = [
        OptimizationResult(
            parameter_id="low",
            fast_window=5,
            slow_window=20,
            total_trades=100,
            win_rate=0.30,
            net_profit=1000,
            average_trade=10,
            profit_factor=1.02,
            expectancy=50,
            max_drawdown=-50000,
            max_drawdown_pct=-0.20,
            final_equity=1_001_000,
            is_baseline=False,
            passes_constraints=True,
        ),
        OptimizationResult(
            parameter_id="high",
            fast_window=10,
            slow_window=40,
            total_trades=100,
            win_rate=0.30,
            net_profit=1500,
            average_trade=15,
            profit_factor=1.01,
            expectancy=80,
            max_drawdown=-60000,
            max_drawdown_pct=-0.25,
            final_equity=1_001_500,
            is_baseline=False,
            passes_constraints=True,
        ),
    ]

    selected = make_optimizer()._select_parameter(results)

    assert selected.parameter_id == "high"


def test_select_parameter_requires_results() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        make_optimizer()._select_parameter([])


def test_wfo_config_generates_expected_windows() -> None:
    timestamps = make_timestamps(100)

    config = WalkForwardOptimizationConfig(
        window_config=WalkForwardConfig(
            train_size=20,
            test_size=10,
            step_size=10,
        )
    )

    from backtest.walk_forward import WalkForwardWindowGenerator

    windows = WalkForwardWindowGenerator(
        config.window_config
    ).generate(timestamps)

    assert len(windows) == 8

    assert windows[0].train_start_index == 0
    assert windows[0].train_end_index == 20
    assert windows[0].test_start_index == 20
    assert windows[0].test_end_index == 30

    assert windows[1].train_start_index == 10
    assert windows[1].train_end_index == 30
    assert windows[1].test_start_index == 30
    assert windows[1].test_end_index == 40


def test_wfo_train_and_test_do_not_overlap() -> None:
    timestamps = make_timestamps(100)

    config = WalkForwardConfig(
        train_size=20,
        test_size=10,
        step_size=10,
    )

    from backtest.walk_forward import WalkForwardWindowGenerator

    windows = WalkForwardWindowGenerator(config).generate(
        timestamps
    )

    for window in windows:
        assert window.train_end_index == window.test_start_index
        assert window.train_end < window.test_start


def test_wfo_uses_fixed_parameter_for_oos() -> None:
    selected = OptimizationResult(
        parameter_id="ema_20_60",
        fast_window=20,
        slow_window=60,
        total_trades=100,
        win_rate=0.30,
        net_profit=1000,
        average_trade=10,
        profit_factor=1.05,
        expectancy=100,
        max_drawdown=-50000,
        max_drawdown_pct=-0.20,
        final_equity=1_001_000,
        is_baseline=True,
        passes_constraints=True,
    )

    optimizer = make_optimizer()

    result = optimizer._select_parameter([selected])

    assert result.parameter_id == "ema_20_60"
    assert result.fast_window == 20
    assert result.slow_window == 60
