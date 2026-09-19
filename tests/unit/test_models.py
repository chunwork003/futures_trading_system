from datetime import date, datetime

from backtest.models import (
    Direction,
    Signal,
    SignalAction,
)


def make_signal(
    action: SignalAction = SignalAction.ENTER,
    direction: Direction = Direction.LONG,
) -> Signal:
    return Signal(
        signal_id="TEST-001",
        timestamp=datetime(2026, 1, 5, 9, 0),
        trade_date=date(2026, 1, 5),
        symbol="TX",
        contract="TXF202601",
        timeframe="1m",
        strategy_id="TEST",
        strategy_version="1.0.0",
        action=action,
        direction=direction,
        entry_price=25000.0,
        quantity=1,
    )


def test_signal_action_defaults_to_enter():
    signal = make_signal()

    assert signal.action == SignalAction.ENTER


def test_signal_action_enter():
    signal = make_signal(
        action=SignalAction.ENTER,
        direction=Direction.LONG,
    )

    assert signal.action == SignalAction.ENTER
    assert signal.direction == Direction.LONG


def test_signal_action_exit():
    signal = make_signal(
        action=SignalAction.EXIT,
        direction=Direction.LONG,
    )

    assert signal.action == SignalAction.EXIT
    assert signal.direction == Direction.LONG


def test_signal_action_reverse():
    signal = make_signal(
        action=SignalAction.REVERSE,
        direction=Direction.SHORT,
    )

    assert signal.action == SignalAction.REVERSE
    assert signal.direction == Direction.SHORT


def test_existing_signal_fields_remain_compatible():
    signal = make_signal()

    assert signal.strategy_id == "TEST"
    assert signal.strategy_version == "1.0.0"
    assert signal.symbol == "TX"
    assert signal.timeframe == "1m"
    assert signal.entry_price == 25000.0
    assert signal.quantity == 1
