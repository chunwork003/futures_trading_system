from datetime import datetime, timedelta

from analysis.drawdown import DrawdownAnalyzer
from analysis.equity import EquityCurve


def make_curve(values: list[float]) -> EquityCurve:
    curve = EquityCurve()
    start = datetime(2026, 1, 1)

    for index, equity in enumerate(values):
        curve.add_snapshot(
            timestamp=start + timedelta(minutes=index),
            equity=equity,
            realized_pnl=equity - 100_000,
            unrealized_pnl=0.0,
        )

    return curve


def test_no_drawdown():
    curve = make_curve([100_000, 101_000, 102_000])

    analyzer = DrawdownAnalyzer(curve)

    assert analyzer.periods() == []
    assert analyzer.maximum_drawdown == 0.0
    assert analyzer.maximum_drawdown_pct == 0.0
    assert analyzer.longest_drawdown_bars == 0
    assert analyzer.longest_recovery_bars is None


def test_recovered_drawdown():
    curve = make_curve(
        [100_000, 105_000, 103_000, 101_000, 106_000]
    )

    analyzer = DrawdownAnalyzer(curve)

    periods = analyzer.periods()

    assert len(periods) == 1

    period = periods[0]

    assert period.peak_equity == 105_000
    assert period.trough_equity == 101_000
    assert period.drawdown == -4_000
    assert period.drawdown_pct == -4_000 / 105_000

    assert period.duration_bars == 2
    assert period.recovery_bars == 1
    assert period.end_time is not None


def test_unrecovered_drawdown():
    curve = make_curve(
        [100_000, 105_000, 103_000, 101_000]
    )

    analyzer = DrawdownAnalyzer(curve)

    periods = analyzer.periods()

    assert len(periods) == 1

    period = periods[0]

    assert period.peak_equity == 105_000
    assert period.trough_equity == 101_000
    assert period.end_time is None
    assert period.recovery_bars is None


def test_multiple_drawdown_periods():
    curve = make_curve(
        [
            100_000,
            105_000,
            103_000,
            105_000,
            102_000,
            101_000,
            106_000,
        ]
    )

    analyzer = DrawdownAnalyzer(curve)

    periods = analyzer.periods()

    assert len(periods) == 2

    assert periods[0].drawdown == -2_000
    assert periods[0].recovery_bars == 1

    assert periods[1].drawdown == -4_000
    assert periods[1].recovery_bars == 1


def test_maximum_drawdown():
    curve = make_curve(
        [100_000, 105_000, 103_000, 101_000, 106_000]
    )

    analyzer = DrawdownAnalyzer(curve)

    assert analyzer.maximum_drawdown == -4_000
    assert analyzer.maximum_drawdown_pct == -4_000 / 105_000


def test_longest_drawdown():
    curve = make_curve(
        [100_000, 105_000, 104_000, 103_000, 101_000, 106_000]
    )

    analyzer = DrawdownAnalyzer(curve)

    assert analyzer.longest_drawdown_bars == 3
    assert analyzer.longest_recovery_bars == 1
