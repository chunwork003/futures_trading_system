from datetime import date, datetime, timedelta

from backtest.engine import BacktestEngine
from backtest.models import (
    BacktestConfig,
    Direction,
    Signal,
    SignalAction,
)


BASE_TIME = datetime(2026, 1, 5, 9, 0)


def make_bar(
    timestamp,
    open_price,
    high_price,
    low_price,
    close_price,
):
    return {
        "timestamp": timestamp,
        "trade_date": date(2026, 1, 5),
        "symbol": "TX",
        "open": open_price,
        "high": high_price,
        "low": low_price,
        "close": close_price,
    }


def make_signal(
    signal_id,
    timestamp,
    action,
    direction=Direction.LONG,
):
    return Signal(
        signal_id=signal_id,
        timestamp=timestamp,
        trade_date=date(2026, 1, 5),
        symbol="TX",
        contract="TXF",
        timeframe="1m",
        strategy_id="TEST",
        strategy_version="1.0",
        action=action,
        direction=direction,
        entry_price=25_000,
        quantity=1,
    )


def make_test_data():
    bars = [
        make_bar(
            BASE_TIME,
            25_000,
            25_020,
            24_990,
            25_010,
        ),
        make_bar(
            BASE_TIME + timedelta(minutes=1),
            25_010,
            25_020,
            25_000,
            25_015,
        ),
        make_bar(
            BASE_TIME + timedelta(minutes=2),
            25_010,
            25_020,
            25_005,
            25_015,
        ),
    ]

    signals = [
        make_signal(
            "SIG-001",
            BASE_TIME,
            SignalAction.ENTER,
        ),
        make_signal(
            "SIG-002",
            BASE_TIME + timedelta(minutes=1),
            SignalAction.EXIT,
        ),
    ]

    return bars, signals


def make_config():
    return BacktestConfig(
        symbol="TX",
        timeframe="1m",
        quantity=1,
        multiplier=200,
        initial_capital=1_000_000,
        commission_per_contract=50,
        slippage_points=1,
        end_of_data_exit=True,
    )


def test_same_engine_repeated_run_is_deterministic():
    bars, signals = make_test_data()

    engine = BacktestEngine(make_config())

    first_trades = engine.run(bars, signals)
    first_trade_models = [
        trade.model_dump()
        for trade in first_trades
    ]

    first_realized_pnl = engine.portfolio.realized_pnl
    first_equity = engine.portfolio.equity
    first_commission = engine.portfolio.commission_paid

    second_trades = engine.run(bars, signals)
    second_trade_models = [
        trade.model_dump()
        for trade in second_trades
    ]

    assert first_trade_models == second_trade_models
    assert engine.portfolio.realized_pnl == first_realized_pnl
    assert engine.portfolio.equity == first_equity
    assert engine.portfolio.commission_paid == first_commission


def test_different_engine_instances_are_deterministic():
    bars, signals = make_test_data()

    engine_a = BacktestEngine(make_config())
    engine_b = BacktestEngine(make_config())

    trades_a = engine_a.run(bars, signals)
    trades_b = engine_b.run(bars, signals)

    assert (
        [trade.model_dump() for trade in trades_a]
        == [trade.model_dump() for trade in trades_b]
    )

    assert engine_a.portfolio.realized_pnl == engine_b.portfolio.realized_pnl
    assert engine_a.portfolio.equity == engine_b.portfolio.equity
    assert engine_a.portfolio.commission_paid == engine_b.portfolio.commission_paid


def test_repeated_run_produces_identical_trade_fields():
    bars, signals = make_test_data()

    engine = BacktestEngine(make_config())

    first_trades = engine.run(bars, signals)
    second_trades = engine.run(bars, signals)

    assert len(first_trades) == len(second_trades)

    for first_trade, second_trade in zip(
        first_trades,
        second_trades,
    ):
        assert first_trade.model_dump() == second_trade.model_dump()


def test_repeated_run_produces_identical_portfolio_state():
    bars, signals = make_test_data()

    engine = BacktestEngine(make_config())

    engine.run(bars, signals)

    first_state = {
        "realized_pnl": engine.portfolio.realized_pnl,
        "unrealized_pnl": engine.portfolio.unrealized_pnl,
        "commission_paid": engine.portfolio.commission_paid,
        "equity": engine.portfolio.equity,
        "position": engine.portfolio.position,
    }

    engine.run(bars, signals)

    second_state = {
        "realized_pnl": engine.portfolio.realized_pnl,
        "unrealized_pnl": engine.portfolio.unrealized_pnl,
        "commission_paid": engine.portfolio.commission_paid,
        "equity": engine.portfolio.equity,
        "position": engine.portfolio.position,
    }

    assert first_state == second_state


def test_changing_input_data_changes_backtest_result():
    bars, signals = make_test_data()

    engine_original = BacktestEngine(make_config())
    original_trades = engine_original.run(
        bars,
        signals,
    )

    modified_bars = list(bars)

    # EXIT signal is generated on T+1
    # and executed at T+2 OPEN.
    modified_bars[2] = make_bar(
        BASE_TIME + timedelta(minutes=2),
        25_015,
        25_020,
        25_005,
        25_015,
    )

    engine_modified = BacktestEngine(make_config())
    modified_trades = engine_modified.run(
        modified_bars,
        signals,
    )

    assert len(original_trades) == 1
    assert len(modified_trades) == 1

    original_trade = original_trades[0]
    modified_trade = modified_trades[0]

    # Regression:
    # EXIT signal generated on T+1
    # must execute at T+2 OPEN.
    #
    # Original:
    # OPEN = 25,010
    # Long exit slippage = 1
    # Actual exit fill = 25,009
    assert original_trade.exit_price == 25_009

    # Modified:
    # OPEN = 25,015
    # Long exit slippage = 1
    # Actual exit fill = 25,014
    assert modified_trade.exit_price == 25_014

    assert (
        original_trade.model_dump()
        != modified_trade.model_dump()
    )

    assert (
        engine_original.portfolio.realized_pnl
        != engine_modified.portfolio.realized_pnl
    )
