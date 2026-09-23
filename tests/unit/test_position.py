from datetime import date, datetime

from backtest.models import Direction, Fill, Signal
from backtest.position import PositionManager


def make_signal() -> Signal:
    return Signal(
        signal_id="SIG-001",
        timestamp=datetime(2026, 1, 1, 9, 0),
        trade_date=date(2026, 1, 1),
        symbol="TXF",
        contract="TXF202601",
        strategy_id="TEST",
        strategy_version="1.0",
        market_state="TREND",
        setup="TEST",
        timeframe="1m",
        entry_type="MARKET",
        entry_price=20000.0,
        action="ENTER",
        direction=Direction.LONG,
        quantity=1,
        stop_price=19900.0,
        target_price=20200.0,
    )


def make_fill(
    price: float,
    quantity: int,
    commission: float,
) -> Fill:
    return Fill(
        order_id="ENTRY-SIG-001",
        timestamp=datetime(2026, 1, 1, 9, 0),
        requested_price=price,
        price=price,
        quantity=quantity,
        commission=commission,
        slippage_points=0.0,
    )


def test_open_position_accumulates_multiple_fills():
    manager = PositionManager()

    position = manager.open_position(
        signal=make_signal(),
        fill=make_fill(
            price=20000.0,
            quantity=1,
            commission=10.0,
        ),
    )

    position = manager.add_fill(
        fill=make_fill(
            price=20010.0,
            quantity=1,
            commission=10.0,
        ),
    )

    assert position.quantity == 2
    assert position.entry_price == 20005.0
    assert position.entry_commission == 20.0


def test_close_position_reduces_quantity_on_partial_fill():
    manager = PositionManager()

    position = manager.open_position(
        signal=make_signal(),
        fill=make_fill(
            price=20000.0,
            quantity=2,
            commission=20.0,
        ),
    )

    position = manager.reduce_position(quantity=1)

    assert position.quantity == 1
    assert manager.current_position is position

def test_short_position_stop_loss():
    manager = PositionManager()

    signal = make_signal().model_copy(
        update={
            "direction": Direction.SHORT,
            "stop_price": 20100.0,
            "target_price": 19800.0,
        }
    )

    manager.open_position(
        signal=signal,
        fill=make_fill(
            price=20000.0,
            quantity=1,
            commission=10.0,
        ),
    )

    reason, exit_price = manager.update_bar(
        timestamp=datetime(2026, 1, 1, 9, 1),
        open_price=20000.0,
        high_price=20150.0,
        low_price=19950.0,
        close_price=20050.0,
    )

    assert reason.name == "SL"
    assert exit_price == 20100.0


def test_short_position_take_profit():
    manager = PositionManager()

    signal = make_signal().model_copy(
        update={
            "direction": Direction.SHORT,
            "stop_price": 20100.0,
            "target_price": 19800.0,
        }
    )

    manager.open_position(
        signal=signal,
        fill=make_fill(
            price=20000.0,
            quantity=1,
            commission=10.0,
        ),
    )

    reason, exit_price = manager.update_bar(
        timestamp=datetime(2026, 1, 1, 9, 1),
        open_price=20000.0,
        high_price=20050.0,
        low_price=19750.0,
        close_price=19800.0,
    )

    assert reason.name == "TP"
    assert exit_price == 19800.0


def test_short_position_intrabar_priority():
    signal = make_signal().model_copy(
        update={
            "direction": Direction.SHORT,
            "stop_price": 20100.0,
            "target_price": 19800.0,
        }
    )

    manager = PositionManager(intrabar_priority="SL_FIRST")

    manager.open_position(
        signal=signal,
        fill=make_fill(
            price=20000.0,
            quantity=1,
            commission=10.0,
        ),
    )

    reason, exit_price = manager.update_bar(
        timestamp=datetime(2026, 1, 1, 9, 1),
        open_price=20000.0,
        high_price=20200.0,
        low_price=19700.0,
        close_price=20000.0,
    )

    assert reason.name == "SL"
    assert exit_price == 20100.0

    manager = PositionManager(intrabar_priority="TP_FIRST")

    manager.open_position(
        signal=signal,
        fill=make_fill(
            price=20000.0,
            quantity=1,
            commission=10.0,
        ),
    )

    reason, exit_price = manager.update_bar(
        timestamp=datetime(2026, 1, 1, 9, 1),
        open_price=20000.0,
        high_price=20200.0,
        low_price=19700.0,
        close_price=20000.0,
    )

    assert reason.name == "TP"
    assert exit_price == 19800.0
