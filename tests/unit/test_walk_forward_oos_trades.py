from datetime import datetime, timedelta

import polars as pl

from backtest.engine import BacktestConfig
from backtest.optimization import OptimizationConstraint, TrendParameterSet
from backtest.walk_forward import WalkForwardConfig
from backtest.walk_forward_optimization import (
    WalkForwardOptimizationConfig,
    WalkForwardOptimizer,
)


def _make_bars(count: int = 200) -> pl.DataFrame:
    start = datetime(2026, 1, 1)

    timestamps = [
        start + timedelta(minutes=index)
        for index in range(count)
    ]

    prices = [100.0 + float(index % 20) for index in range(count)]

    return pl.DataFrame(
        {
            "timestamp": timestamps,
            "trade_date": [
                timestamp.date()
                for timestamp in timestamps
            ],
            "open": prices,
            "high": [price + 1.0 for price in prices],
            "low": [price - 1.0 for price in prices],
            "close": prices,
            "volume": [1] * count,
        }
    )


def _make_optimizer() -> WalkForwardOptimizer:
    backtest_config = BacktestConfig(
        initial_capital=1_000_000,
        symbol="TXF",
        timeframe="1m",
        quantity=1,
        multiplier=200,
    )

    config = WalkForwardOptimizationConfig(
        window_config=WalkForwardConfig(
            train_size=100,
            test_size=50,
            step_size=50,
            expanding=False,
        ),
        parameter_grid=(
            TrendParameterSet(5, 20),
        ),
        constraints=OptimizationConstraint(
            min_trades=0,
            min_profit_factor=0.0,
            max_drawdown_pct=-1000.0,
        ),
    )

    return WalkForwardOptimizer(
        backtest_config=backtest_config,
        config=config,
    )


def test_run_with_trades_returns_same_results_as_run() -> None:
    bars = _make_bars()
    optimizer = _make_optimizer()

    normal_results = optimizer.run(bars)
    detailed_run = optimizer.run_with_trades(bars)

    assert detailed_run.results == normal_results


def test_run_with_trades_returns_actual_trade_objects() -> None:
    bars = _make_bars()
    optimizer = _make_optimizer()

    detailed_run = optimizer.run_with_trades(bars)

    assert all(
        hasattr(trade, "net_pnl")
        for trade in detailed_run.oos_trades
    )


def test_oos_trade_count_matches_window_results() -> None:
    bars = _make_bars()
    optimizer = _make_optimizer()

    detailed_run = optimizer.run_with_trades(bars)

    expected_count = sum(
        result.oos_trades
        for result in detailed_run.results
    )

    assert len(detailed_run.oos_trades) == expected_count


def test_oos_trade_pnl_matches_window_net_profit() -> None:
    bars = _make_bars()
    optimizer = _make_optimizer()

    detailed_run = optimizer.run_with_trades(bars)

    trade_pnl = sum(
        float(trade.net_pnl or 0.0)
        for trade in detailed_run.oos_trades
    )

    window_pnl = sum(
        result.oos_net_profit
        for result in detailed_run.results
    )

    assert trade_pnl == window_pnl
