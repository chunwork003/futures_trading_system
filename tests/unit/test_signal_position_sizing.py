from datetime import date, datetime

from backtest.backtest_sizing_adapter import BacktestSizingAdapter
from backtest.fixed_quantity_sizing import FixedQuantitySizing
from backtest.models import Direction, Signal
from backtest.position_sizing import PositionSizingInput
from backtest.signal_position_sizing import (
    apply_position_sizing_to_signal,
)


def make_signal() -> Signal:
    return Signal(
        signal_id="SIG-001",
        timestamp=datetime(2026, 1, 1, 9, 0),
        trade_date=date(2026, 1, 1),
        symbol="TXF",
        contract="TX1",
        timeframe="1m",
        strategy_id="TEST",
        strategy_version="1.0",
        direction=Direction.LONG,
        entry_price=20_000,
        stop_price=19_900,
        quantity=1,
    )


def test_apply_position_sizing_to_signal_updates_quantity():
    signal = make_signal()

    adapter = BacktestSizingAdapter(
        FixedQuantitySizing(quantity=5)
    )

    sizing_input = PositionSizingInput(
        equity=1_000_000,
        price=20_000,
        stop_price=19_900,
        multiplier=200,
        risk_budget=0.01,
    )

    sized_signal = apply_position_sizing_to_signal(
        signal,
        adapter,
        sizing_input,
    )

    assert signal.quantity == 1
    assert sized_signal.quantity == 5


def test_apply_position_sizing_to_signal_rejects_zero_quantity():
    signal = make_signal()

    adapter = BacktestSizingAdapter(
        FixedQuantitySizing(quantity=1)
    )

    sizing_input = PositionSizingInput(
        equity=1_000_000,
        price=20_000,
        stop_price=19_900,
        multiplier=200,
        risk_budget=0.01,
    )

    sized_signal = apply_position_sizing_to_signal(
        signal,
        adapter,
        sizing_input,
    )

    assert sized_signal.quantity == 1
