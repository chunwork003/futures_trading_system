from datetime import date, datetime

from backtest.engine import BacktestEngine
from backtest.models import (
    BacktestConfig,
    Direction,
    Signal,
)


def test_cost_accounting_with_slippage():

    config = BacktestConfig(
        initial_capital=1_000_000,
        symbol="TX",
        timeframe="1m",
        quantity=1,
        multiplier=200,
        commission_per_contract=50,
        slippage_points=1,
        intrabar_priority="SL_FIRST",
        end_of_data_exit=True,
    )

    engine = BacktestEngine(config)

    bars = [
        {
            "timestamp": datetime(2026, 1, 5, 9, 0),
            "trade_date": date(2026, 1, 5),
            "open": 24990,
            "high": 25000,
            "low": 24980,
            "close": 24995,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 1),
            "trade_date": date(2026, 1, 5),
            "open": 25000,
            "high": 25020,
            "low": 24990,
            "close": 25010,
        },
        {
            "timestamp": datetime(2026, 1, 5, 9, 2),
            "trade_date": date(2026, 1, 5),
            "open": 25010,
            "high": 25050,
            "low": 25000,
            "close": 25040,
        },
    ]

    signals = [
        Signal(
            signal_id="TEST-COST-001",
            timestamp=datetime(2026, 1, 5, 9, 0),
            trade_date=date(2026, 1, 5),
            symbol="TX",
            timeframe="1m",
            strategy_id="TEST",
            strategy_version="v1",
            direction=Direction.LONG,
            market_state="UPTREND",
            setup="ORB",
            entry_type="BREAKOUT",
            entry_price=25000,
            stop_price=24980,
            target_price=25040,
            quantity=1,
        )
    ]

    trades = engine.run(
        bars=bars,
        signals=signals,
    )

    assert len(trades) == 1

    trade = trades[0]

    # Entry:
    # requested = 25000
    # LONG entry slippage = +1
    # actual = 25001
    assert trade.entry_price == 25001

    # Exit:
    # requested = 25040
    # LONG exit slippage = -1
    # actual = 25039
    assert trade.exit_price == 25039

    # Actual price difference:
    # 25039 - 25001 = 38 points
    assert trade.pnl_points == 38

    # 38 × 200 = 7600
    assert trade.gross_pnl == 7600

    # Entry commission 50 + exit commission 50
    assert trade.commission == 100

    # 1 point entry + 1 point exit × 200
    assert trade.slippage_cost == 400

    # IMPORTANT:
    # Slippage is already reflected in actual fill prices.
    # Therefore it must NOT be subtracted again.
    assert trade.net_pnl == 7500

    # Actual risk:
    # 25001 - 24980 = 21 points
    assert trade.risk_points == 21

    # Realized R:
    # 38 / 21
    assert abs(trade.r_multiple - (38 / 21)) < 1e-9

    assert trade.exit_reason.value == "TP"
    assert trade.result == "WIN"

    # MAE:
    # lowest observed = 24990
    # 24990 - 25001 = -11
    assert trade.mae_points == -11

    # MFE:
    # highest observed = 25050
    # 25050 - 25001 = 49
    assert trade.mfe_points == 49

    # 09:01 -> 09:02
    assert trade.holding_minutes == 1

    print()
    print("=== COST ACCOUNTING TEST ===")
    print(f"Entry Price      : {trade.entry_price}")
    print(f"Exit Price       : {trade.exit_price}")
    print(f"PnL Points       : {trade.pnl_points}")
    print(f"Gross PnL        : {trade.gross_pnl}")
    print(f"Commission       : {trade.commission}")
    print(f"Slippage Cost    : {trade.slippage_cost}")
    print(f"Net PnL          : {trade.net_pnl}")
    print(f"Risk Points      : {trade.risk_points}")
    print(f"Realized R       : {trade.r_multiple:.6f}")
    print(f"MAE              : {trade.mae_points}")
    print(f"MFE              : {trade.mfe_points}")
    print(f"Result           : {trade.result}")
    print()
    print("COST ACCOUNTING TEST PASSED")
