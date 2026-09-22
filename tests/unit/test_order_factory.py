from datetime import datetime

from backtest.models import Direction, Signal, SignalAction
from backtest.order_factory import OrderFactory


def test_create_entry_order_from_signal():
    signal = Signal(
        signal_id="SIG-001",
        timestamp=datetime(2026, 1, 5, 9, 0),
        trade_date=datetime(2026, 1, 5).date(),
        symbol="TXF",
        contract="TXF202601",
        timeframe="1m",
        strategy_id="S1",
        strategy_version="1.0.0",
        action=SignalAction.ENTER,
        direction=Direction.LONG,
        market_state="UPTREND",
        setup="TEST",
        entry_type="MARKET",
        entry_price=20000,
        quantity=1,
    )

    order = OrderFactory.create_entry_order(
        signal=signal,
        timestamp=signal.timestamp,
        requested_price=signal.entry_price,
    )

    assert order.order_id == "ENTRY-SIG-001"
    assert order.signal_id == "SIG-001"
    assert order.symbol == "TXF"
    assert order.contract == "TXF202601"
    assert order.direction == Direction.LONG
    assert order.quantity == 1
    assert order.requested_price == 20000
    assert order.status.value == "PENDING"
from datetime import datetime

from backtest.models import Direction, Signal, SignalAction
from backtest.order_factory import OrderFactory


def test_create_exit_order_from_signal():
    signal = Signal(
        signal_id="SIG-EXIT-001",
        timestamp=datetime(2026, 1, 5, 9, 1),
        trade_date=datetime(2026, 1, 5).date(),
        symbol="TXF",
        contract="TXF202601",
        timeframe="1m",
        strategy_id="S1",
        strategy_version="1.0.0",
        action=SignalAction.EXIT,
        direction=Direction.LONG,
        market_state="DOWN",
        setup="TREND_STATE_EXIT_LONG",
        entry_type="MARKET",
        entry_price=20100,
        quantity=1,
    )

    order = OrderFactory.create_exit_order(
        signal=signal,
        timestamp=signal.timestamp,
        requested_price=signal.entry_price,
        quantity=1,
    )

    assert order.order_id == "EXIT-SIG-EXIT-001"
    assert order.signal_id == "SIG-EXIT-001"
    assert order.direction == Direction.LONG
    assert order.quantity == 1
    assert order.requested_price == 20100
    assert order.status.value == "PENDING"
