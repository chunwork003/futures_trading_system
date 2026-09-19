from datetime import date, datetime

from analysis.performance_metrics import PerformanceMetricsAnalyzer
from backtest.models import Direction, ExitReason, Trade


def make_trade(
    trade_id: str,
    net_pnl: float,
    r_multiple: float | None = None,
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
        r_multiple=r_multiple,
    )


def test_empty_trades():
    metrics = PerformanceMetricsAnalyzer([]).calculate()

    assert metrics.profit_factor == 0.0
    assert metrics.expectancy == 0.0
    assert metrics.expectancy_r is None


def test_profit_factor_and_expectancy():
    trades = [
        make_trade("1", 2000.0, 2.0),
        make_trade("2", -1000.0, -1.0),
        make_trade("3", 500.0, 0.5),
        make_trade("4", -500.0, -0.5),
    ]

    metrics = PerformanceMetricsAnalyzer(trades).calculate()

    assert metrics.profit_factor == 2500.0 / 1500.0
    assert metrics.expectancy == 250.0
    assert metrics.expectancy_r == 0.25


def test_profit_factor_with_no_losses():
    trades = [
        make_trade("1", 1000.0, 1.0),
        make_trade("2", 500.0, 0.5),
    ]

    metrics = PerformanceMetricsAnalyzer(trades).calculate()

    assert metrics.profit_factor == float("inf")
    assert metrics.expectancy == 750.0


def test_profit_factor_with_no_winners():
    trades = [
        make_trade("1", -1000.0, -1.0),
        make_trade("2", -500.0, -0.5),
    ]

    metrics = PerformanceMetricsAnalyzer(trades).calculate()

    assert metrics.profit_factor == 0.0
    assert metrics.expectancy == -750.0

def test_profit_factor_with_only_breakeven_trades():
    trades = [
        make_trade("1", 0.0, 0.0),
        make_trade("2", 0.0, 0.0),
    ]

    metrics = PerformanceMetricsAnalyzer(trades).calculate()

    assert metrics.profit_factor == 0.0
    assert metrics.expectancy == 0.0
    assert metrics.expectancy_r == 0.0
