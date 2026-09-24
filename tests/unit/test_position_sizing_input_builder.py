from datetime import date, datetime

from backtest.models import BacktestConfig, Direction, Signal
from backtest.position_sizing_input_builder import (
    build_position_sizing_input,
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
    )


def test_build_position_sizing_input():
    config = BacktestConfig(
        symbol="TXF",
        multiplier=200,
        risk_budget=0.02,
    )

    sizing_input = build_position_sizing_input(
        config=config,
        signal=make_signal(),
        equity=1_000_000,
    )

    assert sizing_input.equity == 1_000_000
    assert sizing_input.price == 20_000
    assert sizing_input.stop_price == 19_900
    assert sizing_input.multiplier == 200
    assert sizing_input.risk_budget == 0.02


def test_build_position_sizing_input_requires_stop_price():
    config = BacktestConfig(symbol="TXF")

    signal = make_signal().model_copy(
        update={"stop_price": None}
    )

    try:
        build_position_sizing_input(
            config=config,
            signal=signal,
            equity=1_000_000,
        )
    except ValueError as exc:
        assert str(exc) == (
            "position sizing requires signal.stop_price"
        )
    else:
        raise AssertionError("ValueError was not raised")
