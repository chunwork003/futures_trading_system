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
    minute: int,
    open_price: float,
    high: float,
    low: float,
    close: float,
):
    timestamp = BASE_TIME + timedelta(minutes=minute)

    return {
        "timestamp": timestamp,
        "trade_date": date(2026, 1, 5),
        "symbol": "TX",
        "contract": "TX202601",
        "timeframe": "1m",
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,
        "volume": 100,
        "session": "DAY",
        "source": "TEST",
    }


def make_signal(
    minute: int,
    direction: Direction,
    action: SignalAction = SignalAction.ENTER,
    stop_price=None,
    target_price=None,
):
    timestamp = BASE_TIME + timedelta(minutes=minute)

    return Signal(
        signal_id=f"SIG-{minute:02d}-{direction.value}-{action.value}",
        timestamp=timestamp,
        trade_date=date(2026, 1, 5),
        symbol="TX",
        contract="TX202601",
        timeframe="1m",
        strategy_id="TEST",
        strategy_version="1.0.0",
        action=action,
        direction=direction,
        market_state="UPTREND",
        setup="TEST_SETUP",
        entry_type="NEXT_BAR_OPEN",
        entry_price=100.0,
        stop_price=stop_price,
        target_price=target_price,
        quantity=1,
    )


def make_config(
    *,
    end_of_data_exit=True,
    slippage_points=0.0,
):
    return BacktestConfig(
        initial_capital=1_000_000,
        symbol="TX",
        timeframe="1m",
        quantity=1,
        multiplier=200,
        commission_per_contract=0.0,
        slippage_points=slippage_points,
        allow_multiple_positions=False,
        intrabar_priority="SL_FIRST",
        end_of_data_exit=end_of_data_exit,
    )


def test_signal_executes_on_next_bar_open():
    bars = [
        make_bar(0, 100, 101, 99, 100),
        make_bar(1, 106, 108, 105, 107),
        make_bar(2, 108, 110, 107, 109),
    ]

    signals = [
        make_signal(0, Direction.LONG),
    ]

    engine = BacktestEngine(make_config())

    trades = engine.run(bars, signals)

    assert len(trades) == 1

    trade = trades[0]

    assert trade.entry_time == BASE_TIME + timedelta(minutes=1)
    assert trade.entry_price == 106.0


def test_long_trade_generates_correct_pnl():
    bars = [
        make_bar(0, 100, 101, 99, 100),
        make_bar(1, 106, 108, 105, 107),
        make_bar(2, 108, 110, 107, 109),
    ]

    signals = [
        make_signal(0, Direction.LONG),
    ]

    engine = BacktestEngine(
        make_config(end_of_data_exit=True)
    )

    trades = engine.run(bars, signals)

    assert len(trades) == 1

    trade = trades[0]

    assert trade.entry_price == 106.0
    assert trade.exit_price == 109.0
    assert trade.pnl_points == 3.0
    assert trade.gross_pnl == 600.0
    assert trade.net_pnl == 600.0
    assert trade.exit_reason == ExitReason.END_OF_DATA


def test_short_trade_generates_correct_pnl():
    bars = [
        make_bar(0, 100, 101, 99, 100),
        make_bar(1, 106, 108, 105, 107),
        make_bar(2, 104, 105, 102, 103),
    ]

    signals = [
        make_signal(0, Direction.SHORT),
    ]

    engine = BacktestEngine(
        make_config(end_of_data_exit=True)
    )

    trades = engine.run(bars, signals)

    assert len(trades) == 1

    trade = trades[0]

    assert trade.entry_price == 106.0
    assert trade.exit_price == 103.0
    assert trade.pnl_points == 3.0
    assert trade.gross_pnl == 600.0


def test_long_stop_loss_is_triggered():
    bars = [
        make_bar(0, 100, 101, 99, 100),
        make_bar(1, 106, 107, 105, 106),
        make_bar(2, 106, 107, 103, 104),
    ]

    signals = [
        make_signal(
            0,
            Direction.LONG,
            stop_price=104,
        ),
    ]

    engine = BacktestEngine(
        make_config(
            end_of_data_exit=True,
        )
    )

    trades = engine.run(bars, signals)

    assert len(trades) == 1

    trade = trades[0]

    assert trade.exit_reason == ExitReason.SL
    assert trade.exit_price == 104.0


def test_long_take_profit_is_triggered():
    bars = [
        make_bar(0, 100, 101, 99, 100),
        make_bar(1, 106, 107, 105, 106),
        make_bar(2, 106, 112, 105, 111),
    ]

    signals = [
        make_signal(
            0,
            Direction.LONG,
            target_price=110,
        ),
    ]

    engine = BacktestEngine(
        make_config(
            end_of_data_exit=True,
        )
    )

    trades = engine.run(bars, signals)

    assert len(trades) == 1

    trade = trades[0]

    assert trade.exit_reason == ExitReason.TP
    assert trade.exit_price == 110.0


def test_no_signal_creates_no_trade():
    bars = [
        make_bar(0, 100, 101, 99, 100),
        make_bar(1, 101, 102, 100, 101),
        make_bar(2, 102, 103, 101, 102),
    ]

    engine = BacktestEngine(make_config())

    trades = engine.run(bars, [])

    assert trades == []


def test_slippage_is_applied_once():
    bars = [
        make_bar(0, 100, 101, 99, 100),
        make_bar(1, 106, 108, 105, 107),
        make_bar(2, 108, 110, 107, 109),
    ]

    signals = [
        make_signal(0, Direction.LONG),
    ]

    engine = BacktestEngine(
        make_config(
            slippage_points=1.0,
            end_of_data_exit=True,
        )
    )

    trades = engine.run(bars, signals)

    assert len(trades) == 1

    trade = trades[0]

    # LONG entry: 106 + 1 = 107
    # LONG exit: 109 - 1 = 108
    assert trade.entry_price == 107.0
    assert trade.exit_price == 108.0

    # Actual fill PnL = 1 point.
    assert trade.pnl_points == 1.0
    assert trade.gross_pnl == 200.0

    # Slippage is informational here and must not
    # be deducted a second time.
    assert trade.slippage_cost == 400.0
    assert trade.net_pnl == 200.0


def test_engine_run_is_deterministic():
    bars = [
        make_bar(0, 100, 101, 99, 100),
        make_bar(1, 106, 108, 105, 107),
        make_bar(2, 108, 110, 107, 109),
    ]

    signals = [
        make_signal(0, Direction.LONG),
    ]

    engine1 = BacktestEngine(make_config())
    engine2 = BacktestEngine(make_config())

    trades1 = engine1.run(bars, signals)
    trades2 = engine2.run(bars, signals)

    assert trades1 == trades2


def test_signal_exit_requires_engine_support():
    bars = [
        make_bar(0, 100, 101, 99, 100),
        make_bar(1, 106, 108, 105, 107),
        make_bar(2, 108, 110, 107, 109),
        make_bar(3, 109, 111, 108, 110),
    ]

    signals = [
        make_signal(0, Direction.LONG),
        make_signal(
            2,
            Direction.LONG,
            action=SignalAction.EXIT,
        ),
    ]

    engine = BacktestEngine(
        make_config(
            end_of_data_exit=True,
        )
    )

    trades = engine.run(bars, signals)

    assert len(trades) == 1

    trade = trades[0]

    assert trade.exit_reason == ExitReason.SIGNAL
    assert trade.exit_time == BASE_TIME + timedelta(minutes=3)
