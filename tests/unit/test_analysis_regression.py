from datetime import datetime, timedelta, timezone

from analysis.equity import EquityCurve
from analysis.performance_report import PerformanceReport
from backtest.models import Direction, ExitReason, Trade


def make_trade(
    trade_id: str,
    net_pnl: float,
    r_multiple: float | None,
) -> Trade:
    entry_time = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc)
    exit_time = entry_time + timedelta(minutes=5)

    return Trade(
        trade_id=trade_id,
        signal_id=f"signal-{trade_id}",
        trade_date=entry_time.date(),
        symbol="TXF",
        contract="TXF",
        timeframe="1m",
        strategy_id="regression",
        strategy_version="1.0",
        direction=Direction.LONG,
        entry_time=entry_time,
        exit_time=exit_time,
        entry_price=25000.0,
        exit_price=25000.0,
        quantity=1,
        gross_pnl=net_pnl,
        commission=0.0,
        slippage_cost=0.0,
        net_pnl=net_pnl,
        r_multiple=r_multiple,
        exit_reason=ExitReason.SIGNAL,
        result=(
            "WIN"
            if net_pnl > 0
            else "LOSS"
            if net_pnl < 0
            else "BREAKEVEN"
        ),
    )


def build_report() -> PerformanceReport:
    trades = [
        make_trade("1", 2000.0, 2.0),
        make_trade("2", -1000.0, -1.0),
        make_trade("3", 500.0, 0.5),
        make_trade("4", -500.0, -0.5),
    ]

    curve = EquityCurve()

    base = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc)

    curve.add_snapshot(
        timestamp=base,
        equity=1_000_000.0,
        realized_pnl=0.0,
        unrealized_pnl=0.0,
    )

    curve.add_snapshot(
        timestamp=base + timedelta(minutes=1),
        equity=1_002_000.0,
        realized_pnl=2000.0,
        unrealized_pnl=0.0,
    )

    curve.add_snapshot(
        timestamp=base + timedelta(minutes=2),
        equity=1_001_000.0,
        realized_pnl=1000.0,
        unrealized_pnl=0.0,
    )

    return PerformanceReport.from_trades(trades, curve)


def test_performance_report_is_deterministic():
    first = build_report()
    second = build_report()

    assert first == second


def test_performance_report_regression_values():
    report = build_report()

    assert report.trade_statistics.total_trades == 4
    assert report.trade_statistics.winning_trades == 2
    assert report.trade_statistics.losing_trades == 2

    assert report.performance_metrics.profit_factor == 2500.0 / 1500.0
    assert report.performance_metrics.expectancy == 250.0
    assert report.performance_metrics.expectancy_r == 0.25

    assert report.final_equity == 1_001_000.0
    assert report.max_drawdown == -1000.0
    assert report.max_drawdown_pct == -1000.0 / 1_002_000.0


def test_performance_report_does_not_mutate_source_data():
    trades = [
        make_trade("1", 1000.0, 1.0),
        make_trade("2", -500.0, -0.5),
    ]

    original_trades = list(trades)

    curve = EquityCurve()
    curve.add_snapshot(
        timestamp=datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
        equity=1_000_000.0,
        realized_pnl=0.0,
        unrealized_pnl=0.0,
    )

    PerformanceReport.from_trades(trades, curve)

    assert trades == original_trades
