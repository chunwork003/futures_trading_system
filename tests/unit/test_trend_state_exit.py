from __future__ import annotations

from datetime import datetime, timedelta

from backtest.models import Direction, SignalAction
from strategies.trend_state_exit import TrendStateExitStrategy


def make_row(
    timestamp: datetime,
    state: str,
    close: float = 100.0,
) -> dict:
    return {
        "timestamp": timestamp,
        "trade_date": timestamp.date(),
        "trend_state": state,
        "close": close,
        "contract": "TXFR1",
    }


def test_long_entry_and_exit() -> None:
    strategy = TrendStateExitStrategy(
        symbol="TXF",
        timeframe="1m",
        quantity=1,
    )

    start = datetime(2026, 1, 1, 9, 0)

    assert strategy.on_bar(
        make_row(start, "SIDEWAYS")
    ) == []

    signals = strategy.on_bar(
        make_row(start + timedelta(minutes=1), "UP")
    )

    assert len(signals) == 1
    assert signals[0].action == SignalAction.ENTER
    assert signals[0].direction == Direction.LONG
    assert signals[0].trade_date == start.date()

    signals = strategy.on_bar(
        make_row(start + timedelta(minutes=2), "WEAKENING")
    )

    assert len(signals) == 1
    assert signals[0].action == SignalAction.EXIT
    assert signals[0].direction == Direction.LONG


def test_short_entry_and_exit() -> None:
    strategy = TrendStateExitStrategy(
        symbol="TXF",
        timeframe="1m",
        quantity=1,
    )

    start = datetime(2026, 1, 1, 9, 0)

    signals = strategy.on_bar(
        make_row(start, "DOWN")
    )

    assert len(signals) == 1
    assert signals[0].action == SignalAction.ENTER
    assert signals[0].direction == Direction.SHORT

    signals = strategy.on_bar(
        make_row(start + timedelta(minutes=1), "STRENGTHENING")
    )

    assert len(signals) == 1
    assert signals[0].action == SignalAction.EXIT
    assert signals[0].direction == Direction.SHORT


def test_no_duplicate_entry_inside_same_trend() -> None:
    strategy = TrendStateExitStrategy(
        symbol="TXF",
        timeframe="1m",
        quantity=1,
    )

    start = datetime(2026, 1, 1, 9, 0)

    signals = strategy.on_bar(
        make_row(start, "UP")
    )

    assert len(signals) == 1
    assert signals[0].action == SignalAction.ENTER
    assert signals[0].direction == Direction.LONG

    assert strategy.on_bar(
        make_row(start + timedelta(minutes=1), "UP")
    ) == []

    assert strategy.on_bar(
        make_row(start + timedelta(minutes=2), "UP")
    ) == []


def test_exit_then_new_direction_can_enter() -> None:
    strategy = TrendStateExitStrategy(
        symbol="TXF",
        timeframe="1m",
        quantity=1,
    )

    start = datetime(2026, 1, 1, 9, 0)

    signals = strategy.on_bar(
        make_row(start, "UP")
    )

    assert signals[0].action == SignalAction.ENTER
    assert signals[0].direction == Direction.LONG

    signals = strategy.on_bar(
        make_row(
            start + timedelta(minutes=1),
            "DOWN",
        )
    )

    assert len(signals) == 1
    assert signals[0].action == SignalAction.EXIT
    assert signals[0].direction == Direction.LONG

    signals = strategy.on_bar(
        make_row(
            start + timedelta(minutes=2),
            "DOWN",
        )
    )

    assert len(signals) == 1
    assert signals[0].action == SignalAction.ENTER
    assert signals[0].direction == Direction.SHORT
