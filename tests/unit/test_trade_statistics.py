from datetime import date, datetime

from backtest.models import Direction, ExitReason, Trade
from analysis.trade_statistics import TradeStatisticsAnalyzer


def make_trade(
    trade_id: str,
    net_pnl: float,
    *,
    holding_minutes: float | None = 30.0,
    r_multiple: float | None = 1.0,
) -> Trade:
    return Trade(
        trade_id=trade_id,
        signal_id=f"signal-{trade_id}",
        trade_date=date(2026, 1, 1),
        symbol="TXF",
        contract="TXF202601",
        timeframe="1m",
        strategy_id="test_strategy",
        strategy_version="1.0",
        direction=Direction.LONG,
        entry_time=datetime(2026, 1, 1, 9, 0),
        exit_time=datetime(2026, 1, 1, 9, 30),
        entry_price=25000.0,
        exit_price=25010.0,
        quantity=1,
        gross_pnl=net_pnl,
        commission=0.0,
        slippage_cost=0.0,
        net_pnl=net_pnl,
        exit_reason=ExitReason.SIGNAL,
        result="WIN" if net_pnl > 0 else "LOSS" if net_pnl < 0 else "BREAKEVEN",
        holding_minutes=holding_minutes,
        r_multiple=r_multiple,
    )


def test_empty_trades():
    stats = TradeStatisticsAnalyzer([]).calculate()

    assert stats.total_trades == 0
    assert stats.win_rate == 0.0
    assert stats.net_profit == 0.0
    assert stats.average_holding_minutes is None
    assert stats.average_r_multiple is None


def test_trade_statistics():
    trades = [
        make_trade("1", 2000.0, holding_minutes=20.0, r_multiple=2.0),
        make_trade("2", -1000.0, holding_minutes=40.0, r_multiple=-1.0),
        make_trade("3", 500.0, holding_minutes=60.0, r_multiple=0.5),
        make_trade("4", 0.0, holding_minutes=10.0, r_multiple=0.0),
    ]

    stats = TradeStatisticsAnalyzer(trades).calculate()

    assert stats.total_trades == 4
    assert stats.winning_trades == 2
    assert stats.losing_trades == 1
    assert stats.breakeven_trades == 1

    assert stats.win_rate == 0.5

    assert stats.gross_profit == 2500.0
    assert stats.gross_loss == -1000.0
    assert stats.net_profit == 1500.0

    assert stats.average_trade == 375.0
    assert stats.average_winner == 1250.0
    assert stats.average_loser == -1000.0

    assert stats.largest_winner == 2000.0
    assert stats.largest_loser == -1000.0

    assert stats.average_holding_minutes == 32.5
    assert stats.average_r_multiple == 0.375


def test_statistics_ignore_missing_optional_values():
    trades = [
        make_trade("1", 1000.0, holding_minutes=None, r_multiple=None),
        make_trade("2", -500.0, holding_minutes=20.0, r_multiple=-0.5),
    ]

    stats = TradeStatisticsAnalyzer(trades).calculate()

    assert stats.average_holding_minutes == 20.0
    assert stats.average_r_multiple == -0.5
