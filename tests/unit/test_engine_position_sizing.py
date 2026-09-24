from datetime import date, datetime

from backtest.engine import BacktestEngine
from backtest.fixed_quantity_sizing import FixedQuantitySizing
from backtest.models import BacktestConfig, Direction, Signal
from backtest.risk import RiskConfig


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


def test_backtest_engine_uses_position_sizing_strategy():
    config = BacktestConfig(
        symbol="TXF",
        multiplier=200,
        risk_config=RiskConfig(
            max_contracts=3,
        ),
    )

    engine = BacktestEngine(
        config=config,
        position_sizing_strategy=FixedQuantitySizing(quantity=3),
    )

    bars = [
        {
            "timestamp": datetime(2026, 1, 1, 9, 0),
            "trade_date": date(2026, 1, 1),
            "symbol": "TXF",
            "open": 20_000,
            "high": 20_050,
            "low": 19_950,
            "close": 20_000,
        },
        {
            "timestamp": datetime(2026, 1, 1, 9, 1),
            "trade_date": date(2026, 1, 1),
            "symbol": "TXF",
            "open": 20_000,
            "high": 20_050,
            "low": 19_950,
            "close": 20_000,
        },
        {
            "timestamp": datetime(2026, 1, 1, 9, 2),
            "trade_date": date(2026, 1, 1),
            "symbol": "TXF",
            "open": 20_000,
            "high": 20_050,
            "low": 19_950,
            "close": 20_000,
        },
    ]

    trades = engine.run(
        bars=bars,
        signals=[make_signal()],
    )

    assert len(trades) == 1
    assert trades[0].quantity == 3
