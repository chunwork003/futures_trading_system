from datetime import date, datetime

from backtest.engine import BacktestEngine
from backtest.fixed_risk_sizing import FixedRiskSizing
from backtest.models import BacktestConfig, Direction, Signal, SignalAction
from backtest.risk import RiskConfig


def test_engine_applies_fixed_risk_position_sizing():
    config = BacktestConfig(
        symbol="TXF",
        multiplier=200,
        risk_budget=0.01,
        risk_config=RiskConfig(
            max_contracts=3,
        ),
    )

    engine = BacktestEngine(
        config,
        position_sizing_strategy=FixedRiskSizing(),
    )

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
            "open": 20000,
            "high": 20020,
            "low": 19980,
            "close": 20000,
        },
        {
            "timestamp": datetime(2024, 1, 1, 9, 2),
            "trade_date": trade_date,
            "open": 20000,
            "high": 20020,
            "low": 19980,
            "close": 20000,
        },
    ]

    signals = [
        Signal(
            signal_id="test-fixed-risk-1",
            timestamp=bars[0]["timestamp"],
            trade_date=trade_date,
            timeframe="1m",
            symbol="TXF",
            strategy_id="test-strategy",
            strategy_version="1.0",
            action=SignalAction.ENTER,
            direction=Direction.LONG,
            entry_price=20000,
            stop_price=19980,
            quantity=1,
        )
    ]

    trades = engine.run(bars, signals)

    assert len(trades) == 1
    assert trades[0].quantity == 2
