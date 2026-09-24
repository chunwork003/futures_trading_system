from datetime import date, datetime

from backtest.fixed_quantity_sizing import FixedQuantitySizing
from backtest.fixed_risk_sizing import FixedRiskSizing
from backtest.models import (
    BacktestConfig,
    Direction,
    Signal,
    SignalAction,
)
from backtest.sizing_comparison_runner import SizingComparisonRunner


def make_bars() -> list[dict]:
    return [
        {
            "timestamp": datetime(2025, 1, 2, 9, 0),
            "trade_date": date(2025, 1, 2),
            "symbol": "TXF",
            "open": 20000,
            "high": 20000,
            "low": 20000,
            "close": 20000,
            "volume": 1,
        },
        {
            "timestamp": datetime(2025, 1, 2, 9, 1),
            "trade_date": date(2025, 1, 2),
            "symbol": "TXF",
            "open": 20100,
            "high": 20100,
            "low": 20100,
            "close": 20100,
            "volume": 1,
        },
        {
            "timestamp": datetime(2025, 1, 2, 9, 2),
            "trade_date": date(2025, 1, 2),
            "symbol": "TXF",
            "open": 20200,
            "high": 20200,
            "low": 20200,
            "close": 20200,
            "volume": 1,
        },
    ]


def make_signals() -> list[Signal]:
    return [
        Signal(
            signal_id="SIG-1",
            timestamp=datetime(2025, 1, 2, 9, 0),
            symbol="TXF",
            direction=Direction.LONG,
            action=SignalAction.ENTER,
            entry_price=20000,
            stop_price=19900,
            strategy_id="test",
            strategy_version="1.0",
            trade_date=date(2025, 1, 2),
            timeframe="1m",
            quantity=1,
        )
    ]


def test_sizing_comparison_runner_compares_multiple_strategies():
    config = BacktestConfig(
        symbol="TXF",
        initial_capital=1_000_000,
        multiplier=200,
        risk_budget=0.02,
    )

    runner = SizingComparisonRunner(
        strategies={
            "fixed_quantity": FixedQuantitySizing(quantity=1),
            "fixed_risk": FixedRiskSizing(),
        }
    )

    results = runner.run(
        config=config,
        bars=make_bars(),
        signals=make_signals(),
    )

    assert set(results) == {
        "fixed_quantity",
        "fixed_risk",
    }

    assert results["fixed_quantity"].total_trades == 1
    assert results["fixed_risk"].total_trades == 1

    assert results["fixed_quantity"].net_pnl == 20_000
    assert results["fixed_risk"].net_pnl == 20_000
