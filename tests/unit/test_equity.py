from datetime import datetime, timedelta

from analysis.equity import EquityCurve


def test_empty_equity_curve():
    curve = EquityCurve()

    assert curve.snapshots == []
    assert curve.final_equity is None
    assert curve.max_drawdown == 0.0
    assert curve.max_drawdown_pct == 0.0


def test_equity_curve_without_drawdown():
    curve = EquityCurve()
    start = datetime(2026, 1, 1, 9, 0)

    curve.add_snapshot(
        timestamp=start,
        equity=1_000_000,
        realized_pnl=0,
        unrealized_pnl=0,
    )

    curve.add_snapshot(
        timestamp=start + timedelta(minutes=1),
        equity=1_001_000,
        realized_pnl=0,
        unrealized_pnl=1_000,
    )

    curve.add_snapshot(
        timestamp=start + timedelta(minutes=2),
        equity=1_002_000,
        realized_pnl=2_000,
        unrealized_pnl=0,
    )

    assert [s.peak_equity for s in curve.snapshots] == [
        1_000_000,
        1_001_000,
        1_002_000,
    ]

    assert [s.drawdown for s in curve.snapshots] == [
        0,
        0,
        0,
    ]

    assert curve.max_drawdown == 0
    assert curve.max_drawdown_pct == 0
    assert curve.final_equity == 1_002_000


def test_equity_curve_drawdown():
    curve = EquityCurve()
    start = datetime(2026, 1, 1, 9, 0)

    values = [
        1_000_000,
        1_010_000,
        995_000,
        998_000,
        1_020_000,
    ]

    for index, equity in enumerate(values):
        curve.add_snapshot(
            timestamp=start + timedelta(minutes=index),
            equity=equity,
            realized_pnl=equity - 1_000_000,
            unrealized_pnl=0,
        )

    assert [s.peak_equity for s in curve.snapshots] == [
        1_000_000,
        1_010_000,
        1_010_000,
        1_010_000,
        1_020_000,
    ]

    assert [s.drawdown for s in curve.snapshots] == [
        0,
        0,
        -15_000,
        -12_000,
        0,
    ]

    assert curve.max_drawdown == -15_000
    assert curve.max_drawdown_pct == -15_000 / 1_010_000


def test_equity_curve_recovers_and_updates_peak():
    curve = EquityCurve()
    start = datetime(2026, 1, 1, 9, 0)

    values = [
        1_000_000,
        1_010_000,
        995_000,
        1_020_000,
    ]

    for index, equity in enumerate(values):
        curve.add_snapshot(
            timestamp=start + timedelta(minutes=index),
            equity=equity,
            realized_pnl=0,
            unrealized_pnl=equity - 1_000_000,
        )

    assert curve.snapshots[2].drawdown == -15_000
    assert curve.snapshots[3].peak_equity == 1_020_000
    assert curve.snapshots[3].drawdown == 0


def test_equity_curve_tracks_unrealized_pnl():
    curve = EquityCurve()
    timestamp = datetime(2026, 1, 1, 9, 0)

    snapshot = curve.add_snapshot(
        timestamp=timestamp,
        equity=999_800,
        realized_pnl=0,
        unrealized_pnl=-200,
    )

    assert snapshot.equity == 999_800
    assert snapshot.realized_pnl == 0
    assert snapshot.unrealized_pnl == -200
    assert snapshot.drawdown == 0


def test_equity_curve_from_snapshots():
    start = datetime(2026, 1, 1, 9, 0)

    curve = EquityCurve.from_snapshots(
        [
            (start, 1_000_000, 0, 0),
            (start + timedelta(minutes=1), 1_001_000, 0, 1_000),
            (start + timedelta(minutes=2), 999_000, -1_000, 0),
        ]
    )

    assert len(curve.snapshots) == 3
    assert curve.final_equity == 999_000
    assert curve.max_drawdown == -2_000
