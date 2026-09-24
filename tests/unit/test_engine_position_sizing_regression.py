from datetime import date, datetime

from backtest.engine import BacktestEngine
from backtest.models import BacktestConfig, Direction, Signal, SignalAction


def test_engine_without_position_sizing_strategy_preserves_signal_quantity():
    config = BacktestConfig(
        symbol="TXF",
        multiplier=200,
    )

    engine = BacktestEngine(config)

    trade_date = date(2024, 1, 1)

    bars = [
        {
            "timestamp": datetime(2024, 1, 1, 9, 0),
            "trade_date": trade_date,
            "open": 20000,
            "high": 20010,
            "low": 19990,
            "close": 20000,
        },
        {
            "timestamp": datetime(2024, 1, 1, 9, 1),
            "trade_date": trade_date,
            "open": 20010,
            "high": 20020,
            "low": 20000,
            "close": 20010,
        },
        {
            "timestamp": datetime(2024, 1, 1, 9, 2),
            "trade_date": trade_date,
            "open": 20020,
            "high": 20030,
            "low": 20010,
            "close": 20020,
        },
    ]

    signals = [
        Signal(
            signal_id="test-signal-1",
            timestamp=bars[0]["timestamp"],
            trade_date=trade_date,
            timeframe="1m",
            symbol="TXF",
            strategy_id="test-strategy",
            strategy_version="1.0",
            action=SignalAction.ENTER,
            direction=Direction.LONG,
            entry_price=20000,
            quantity=1,
        )
    ]

    trades = engine.run(bars, signals)

    assert len(trades) == 1
    assert trades[0].quantity == 1
