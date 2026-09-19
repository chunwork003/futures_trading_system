from datetime import date, datetime, timedelta

from backtest.engine import BacktestEngine
from backtest.models import (
    BacktestConfig,
    Direction,
    ExitReason,
    Signal,
    SignalAction,
)


BASE_TIME = datetime(2026, 1, 5, 9, 0)


def make_bar(
    timestamp: datetime,
    open_price: float,
    high_price: float,
    low_price: float,
    close_price: float,
) -> dict:
    return {
        "timestamp": timestamp,
        "trade_date": date(2026, 1, 5),
        "open": open_price,
        "high": high_price,
        "low": low_price,
        "close": close_price,
    }


def make_signal(
    signal_id: str,
    timestamp: datetime,
    action: SignalAction,
    direction: Direction,
    quantity: int = 1,
) -> Signal:
    return Signal(
        signal_id=signal_id,
        timestamp=timestamp,
        trade_date=date(2026, 1, 5),
        symbol="TX",
        contract=None,
        timeframe="1m",
        strategy_id="TEST",
        strategy_version="1.0",
        action=action,
        direction=direction,
        entry_price=25_000,
        quantity=quantity,
    )


def make_config(
    commission_per_contract: float = 50,
) -> BacktestConfig:
    return BacktestConfig(
        initial_capital=1_000_000,
        symbol="TX",
        timeframe="1m",
        quantity=1,
        multiplier=200,
        commission_per_contract=commission_per_contract,
        slippage_points=0,
        end_of_data_exit=True,
    )


def test_long_trade_portfolio_matches_trade_pnl():
    bars = [
        make_bar(
            BASE_TIME,
            25_000,
            25_005,
            24_995,
            25_000,
        ),
        make_bar(
            BASE_TIME + timedelta(minutes=1),
            25_000,
            25_010,
            24_998,
            25_005,
        ),
        make_bar(
            BASE_TIME + timedelta(minutes=2),
            25_010,
            25_015,
            25_005,
            25_010,
        ),
    ]

    signals = [
        make_signal(
            "SIG-001",
            BASE_TIME,
            SignalAction.ENTER,
            Direction.LONG,
        ),
        make_signal(
            "SIG-002",
            BASE_TIME + timedelta(minutes=1),
            SignalAction.EXIT,
            Direction.LONG,
        ),
    ]

    engine = BacktestEngine(
        make_config(commission_per_contract=50)
    )

    trades = engine.run(bars, signals)

    assert len(trades) == 1

    trade = trades[0]

    assert trade.entry_price == 25_000
    assert trade.exit_price == 25_010

    assert trade.gross_pnl == 2_000
    assert trade.commission == 100
    assert trade.net_pnl == 1_900

    assert engine.portfolio.realized_pnl == 1_900
    assert engine.portfolio.unrealized_pnl == 0
    assert engine.portfolio.equity == 1_001_900
    assert engine.portfolio.commission_paid == 100
    assert engine.portfolio.position is None

    assert trade.net_pnl == engine.portfolio.realized_pnl
    assert trade.exit_reason == ExitReason.SIGNAL


def test_short_trade_portfolio_matches_trade_pnl():
    bars = [
        make_bar(
            BASE_TIME,
            25_000,
            25_005,
            24_995,
            25_000,
        ),
        make_bar(
            BASE_TIME + timedelta(minutes=1),
            25_000,
            25_002,
            24_990,
            24_995,
        ),
        make_bar(
            BASE_TIME + timedelta(minutes=2),
            24_990,
            24_995,
            24_980,
            24_990,
        ),
    ]

    signals = [
        make_signal(
            "SIG-001",
            BASE_TIME,
            SignalAction.ENTER,
            Direction.SHORT,
        ),
        make_signal(
            "SIG-002",
            BASE_TIME + timedelta(minutes=1),
            SignalAction.EXIT,
            Direction.SHORT,
        ),
    ]

    engine = BacktestEngine(
        make_config(commission_per_contract=50)
    )

    trades = engine.run(bars, signals)

    assert len(trades) == 1

    trade = trades[0]

    assert trade.entry_price == 25_000
    assert trade.exit_price == 24_990

    assert trade.gross_pnl == 2_000
    assert trade.commission == 100
    assert trade.net_pnl == 1_900

    assert engine.portfolio.realized_pnl == 1_900
    assert engine.portfolio.equity == 1_001_900
    assert engine.portfolio.commission_paid == 100
    assert engine.portfolio.position is None

    assert trade.net_pnl == engine.portfolio.realized_pnl


def test_portfolio_uses_actual_fill_price_with_slippage():
    bars = [
        make_bar(
            BASE_TIME,
            25_000,
            25_005,
            24_995,
            25_000,
        ),
        make_bar(
            BASE_TIME + timedelta(minutes=1),
            25_000,
            25_010,
            24_998,
            25_005,
        ),
        make_bar(
            BASE_TIME + timedelta(minutes=2),
            25_010,
            25_020,
            25_005,
            25_010,
        ),
    ]

    signals = [
        make_signal(
            "SIG-001",
            BASE_TIME,
            SignalAction.ENTER,
            Direction.LONG,
        ),
        make_signal(
            "SIG-002",
            BASE_TIME + timedelta(minutes=1),
            SignalAction.EXIT,
            Direction.LONG,
        ),
    ]

    engine = BacktestEngine(
        BacktestConfig(
            initial_capital=1_000_000,
            symbol="TX",
            timeframe="1m",
            quantity=1,
            multiplier=200,
            commission_per_contract=0,
            slippage_points=1,
            end_of_data_exit=True,
        )
    )

    trades = engine.run(bars, signals)

    assert len(trades) == 1

    trade = trades[0]

    # Long entry:
    # requested 25,000 -> fill 25,001
    #
    # Long exit:
    # requested 25,010 -> fill 25,009
    #
    # Therefore:
    # pnl = (25,009 - 25,001) * 200 = 1,600
    assert trade.entry_price == 25_001
    assert trade.exit_price == 25_009
    assert trade.gross_pnl == 1_600
    assert trade.net_pnl == 1_600

    assert engine.portfolio.realized_pnl == 1_600
    assert engine.portfolio.equity == 1_001_600


def test_portfolio_is_reset_between_engine_runs():
    bars = [
        make_bar(
            BASE_TIME,
            25_000,
            25_005,
            24_995,
            25_000,
        ),
        make_bar(
            BASE_TIME + timedelta(minutes=1),
            25_000,
            25_010,
            24_998,
            25_005,
        ),
        make_bar(
            BASE_TIME + timedelta(minutes=2),
            25_010,
            25_015,
            25_005,
            25_010,
        ),
    ]

    signals = [
        make_signal(
            "SIG-001",
            BASE_TIME,
            SignalAction.ENTER,
            Direction.LONG,
        ),
        make_signal(
            "SIG-002",
            BASE_TIME + timedelta(minutes=1),
            SignalAction.EXIT,
            Direction.LONG,
        ),
    ]

    engine = BacktestEngine(
        make_config(commission_per_contract=50)
    )

    first_run = engine.run(bars, signals)

    assert len(first_run) == 1
    assert engine.portfolio.realized_pnl == 1_900
    assert engine.portfolio.equity == 1_001_900

    second_run = engine.run(bars, signals)

    assert len(second_run) == 1
    assert engine.portfolio.realized_pnl == 1_900
    assert engine.portfolio.equity == 1_001_900
    assert engine.portfolio.commission_paid == 100
    assert engine.portfolio.position is None


def test_open_position_is_marked_to_market():
    bars = [
        make_bar(
            BASE_TIME,
            25_000,
            25_005,
            24_995,
            25_000,
        ),
        make_bar(
            BASE_TIME + timedelta(minutes=1),
            25_000,
            25_020,
            24_998,
            25_010,
        ),
    ]

    signals = [
        make_signal(
            "SIG-001",
            BASE_TIME,
            SignalAction.ENTER,
            Direction.LONG,
        ),
    ]

    config = make_config(commission_per_contract=0)
    config.end_of_data_exit = False

    engine = BacktestEngine(config)

    trades = engine.run(bars, signals)

    assert trades == []

    # Entry is executed at second bar open = 25,000.
    # Final bar closes at 25,010.
    #
    # Unrealized:
    # (25,010 - 25,000) * 200 = 2,000
    assert engine.portfolio.position is not None
    assert engine.portfolio.unrealized_pnl == 2_000
    assert engine.portfolio.realized_pnl == 0
    assert engine.portfolio.equity == 1_002_000
