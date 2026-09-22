from datetime import date, datetime

from backtest.engine import BacktestEngine
from backtest.models import BacktestConfig, Direction, ExitReason, Signal, SignalAction
from backtest.risk import RiskConfig


def test_engine_forces_liquidation_when_equity_below_maintenance_margin():
    engine = BacktestEngine(
        BacktestConfig(
            symbol="TX",
            initial_capital=100_000,
            risk_config=RiskConfig(
                initial_margin_per_contract=90_000,
                maintenance_margin_per_contract=20_000,
                max_contracts=1,
                max_margin_utilization=1.0,
            ),
        )
    )

    signal = Signal(
        signal_id="SIG-001",
        timestamp=datetime(2025, 1, 2, 9, 0),
        trade_date=date(2025, 1, 2),
        symbol="TX",
        contract="TX",
        timeframe="1m",
        strategy_id="TEST",
        strategy_version="1.0",
        action=SignalAction.ENTER,
        direction=Direction.LONG,
        quantity=1,
        entry_price=20_000,
    )

    bars = [
        {
            "timestamp": datetime(2025, 1, 2, 9, 0),
            "trade_date": date(2025, 1, 2),
            "open": 20_000,
            "high": 20_000,
            "low": 20_000,
            "close": 20_000,
        },
        {
            "timestamp": datetime(2025, 1, 2, 9, 1),
            "trade_date": date(2025, 1, 2),
            "open": 20_000,
            "high": 20_000,
            "low": 19_550,
            "close": 19_550,
        },
    ]

    engine.run(bars=bars, signals=[signal])

    assert engine.position_manager.is_flat
    assert len(engine.trades) == 1
    assert engine.trades[0].exit_reason == ExitReason.FORCED_LIQUIDATION



