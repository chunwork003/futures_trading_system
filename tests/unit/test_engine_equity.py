from datetime import datetime

from backtest.engine import BacktestEngine
from backtest.models import BacktestConfig


def make_bars():
    return [
        {
            "timestamp": datetime(2026, 1, 5, 9, 0),
            "open": 25000,
            "high": 25010,
            "low": 24990,
            "close": 25005,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "open": 25005,
            "high": 25020,
            "low": 25000,
            "close": 25015,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 2),
            "open": 25015,
            "high": 25030,
            "low": 25010,
            "close": 25025,
        },
    ]


def make_engine():
    config = BacktestConfig(
        initial_capital=1_000_000,
        symbol="TXF",
        timeframe="1m",
        quantity=1,
        multiplier=200,
    )
    return BacktestEngine(config)


def test_engine_records_one_equity_snapshot_per_bar():
    engine = make_engine()

    engine.run(make_bars(), [])

    assert len(engine.equity_curve.snapshots) == 3


def test_engine_equity_curve_has_bar_timestamps():
    engine = make_engine()

    engine.run(make_bars(), [])

    timestamps = [
        snapshot.timestamp
        for snapshot in engine.equity_curve.snapshots
    ]

    assert timestamps == [
        datetime(2026, 1, 5, 9, 0),
        datetime(2026, 1, 5, 9, 1),
        datetime(2026, 1, 5, 9, 2),
    ]


def test_engine_equity_curve_starts_at_initial_capital():
    engine = make_engine()

    engine.run(make_bars(), [])

    first = engine.equity_curve.snapshots[0]

    assert first.equity == 1_000_000
    assert first.realized_pnl == 0
    assert first.unrealized_pnl == 0


def test_engine_equity_curve_is_reset_between_runs():
    engine = make_engine()

    engine.run(make_bars(), [])
    first_run = list(engine.equity_curve.snapshots)

    engine.run(make_bars(), [])
    second_run = list(engine.equity_curve.snapshots)

    assert first_run == second_run
    assert len(second_run) == 3
