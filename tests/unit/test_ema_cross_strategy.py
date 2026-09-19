from datetime import date, datetime, timedelta

from backtest.models import Direction, SignalAction
from strategies.ema_cross import EMACrossStrategy


def make_row(
    index: int,
    ema20: float | None,
    ema60: float | None,
) -> dict:
    timestamp = datetime(2026, 1, 5, 9, 0) + timedelta(minutes=index)

    return {
        "timestamp": timestamp,
        "trade_date": date(2026, 1, 5),
        "symbol": "TX",
        "contract": "TXF202601",
        "close": 25000.0 + index,
        "ema_20": ema20,
        "ema_60": ema60,
    }


def test_no_signal_during_ema_warmup():
    strategy = EMACrossStrategy(symbol="TX")

    assert strategy.on_bar(
        make_row(0, None, None)
    ) == []

    assert strategy.on_bar(
        make_row(1, None, None)
    ) == []


def test_first_valid_ema_does_not_create_signal():
    strategy = EMACrossStrategy(symbol="TX")

    assert strategy.on_bar(
        make_row(0, 100.0, 100.0)
    ) == []


def test_cross_up_generates_long_signal():
    strategy = EMACrossStrategy(symbol="TX")

    strategy.on_bar(
        make_row(0, 100.0, 100.0)
    )

    signals = strategy.on_bar(
        make_row(1, 101.0, 100.0)
    )

    assert len(signals) == 1

    signal = signals[0]

    assert signal.action == SignalAction.ENTER
    assert signal.direction == Direction.LONG
    assert signal.strategy_id == "EMA_CROSS"
    assert signal.strategy_version == "1.0.0"
    assert signal.setup == "EMA20_EMA60_CROSS"
    assert signal.entry_type == "NEXT_BAR_OPEN"


def test_cross_down_generates_short_signal():
    strategy = EMACrossStrategy(symbol="TX")

    strategy.on_bar(
        make_row(0, 100.0, 100.0)
    )

    signals = strategy.on_bar(
        make_row(1, 99.0, 100.0)
    )

    assert len(signals) == 1

    signal = signals[0]

    assert signal.action == SignalAction.ENTER
    assert signal.direction == Direction.SHORT


def test_no_repeated_signal_without_new_cross():
    strategy = EMACrossStrategy(symbol="TX")

    assert strategy.on_bar(
        make_row(0, 100.0, 100.0)
    ) == []

    assert len(
        strategy.on_bar(
            make_row(1, 101.0, 100.0)
        )
    ) == 1

    assert strategy.on_bar(
        make_row(2, 102.0, 100.0)
    ) == []

    assert strategy.on_bar(
        make_row(3, 103.0, 100.0)
    ) == []


def test_cross_sequence_generates_only_cross_events():
    strategy = EMACrossStrategy(symbol="TX")

    rows = [
        make_row(0, 100.0, 100.0),
        make_row(1, 101.0, 100.0),
        make_row(2, 102.0, 100.0),
        make_row(3, 99.0, 100.0),
        make_row(4, 98.0, 100.0),
        make_row(5, 101.0, 100.0),
    ]

    signals = []

    for row in rows:
        signals.extend(strategy.on_bar(row))

    assert len(signals) == 3

    assert signals[0].direction == Direction.LONG
    assert signals[1].direction == Direction.SHORT
    assert signals[2].direction == Direction.LONG


def test_signal_uses_current_completed_bar_only():
    strategy = EMACrossStrategy(symbol="TX")

    first = make_row(0, 100.0, 100.0)
    second = make_row(1, 101.0, 100.0)

    assert strategy.on_bar(first) == []

    signals = strategy.on_bar(second)

    assert len(signals) == 1

    signal = signals[0]

    assert signal.timestamp == second["timestamp"]
    assert signal.entry_price == second["close"]


def test_future_data_does_not_change_previous_signal():
    rows = [
        make_row(0, 100.0, 100.0),
        make_row(1, 101.0, 100.0),
        make_row(2, 102.0, 100.0),
        make_row(3, 99.0, 100.0),
    ]

    strategy_a = EMACrossStrategy(symbol="TX")
    signals_a = []

    for row in rows:
        signals_a.extend(strategy_a.on_bar(row))

    strategy_b = EMACrossStrategy(symbol="TX")
    signals_b = []

    for row in rows[:3]:
        signals_b.extend(strategy_b.on_bar(row))

    assert len(signals_a) >= 1
    assert len(signals_b) == 1

    assert signals_a[0].signal_id == signals_b[0].signal_id
    assert signals_a[0].timestamp == signals_b[0].timestamp
    assert signals_a[0].direction == signals_b[0].direction
