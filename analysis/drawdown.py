from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from analysis.equity import EquityCurve


@dataclass(frozen=True)
class DrawdownPeriod:
    start_time: datetime
    trough_time: datetime
    end_time: datetime | None

    peak_equity: float
    trough_equity: float
    drawdown: float
    drawdown_pct: float

    duration_bars: int
    recovery_bars: int | None


class DrawdownAnalyzer:
    """Analyze drawdown periods from an EquityCurve."""

    def __init__(self, equity_curve: EquityCurve) -> None:
        self.equity_curve = equity_curve

    def periods(self) -> list[DrawdownPeriod]:
        snapshots = self.equity_curve.snapshots

        if not snapshots:
            return []

        periods: list[DrawdownPeriod] = []

        peak_index = 0
        trough_index = 0
        start_index: int | None = None
        in_drawdown = False

        for index, snapshot in enumerate(snapshots):
            peak_equity = snapshots[peak_index].equity

            # New/equal equity peak means the previous drawdown is recovered.
            if snapshot.equity >= peak_equity:
                if in_drawdown and start_index is not None:
                    peak = snapshots[peak_index]
                    trough = snapshots[trough_index]

                    periods.append(
                        DrawdownPeriod(
                            start_time=peak.timestamp,
                            trough_time=trough.timestamp,
                            end_time=snapshot.timestamp,
                            peak_equity=peak.equity,
                            trough_equity=trough.equity,
                            drawdown=trough.drawdown,
                            drawdown_pct=trough.drawdown_pct,
                            duration_bars=trough_index - peak_index,
                            recovery_bars=index - trough_index,
                        )
                    )

                peak_index = index
                trough_index = index
                start_index = None
                in_drawdown = False
                continue

            # Equity is below the current peak.
            if not in_drawdown:
                start_index = peak_index
                trough_index = index
                in_drawdown = True
            elif snapshot.equity < snapshots[trough_index].equity:
                trough_index = index

        # Drawdown that has not recovered by the end of the test.
        if in_drawdown and start_index is not None:
            peak = snapshots[peak_index]
            trough = snapshots[trough_index]

            periods.append(
                DrawdownPeriod(
                    start_time=peak.timestamp,
                    trough_time=trough.timestamp,
                    end_time=None,
                    peak_equity=peak.equity,
                    trough_equity=trough.equity,
                    drawdown=trough.drawdown,
                    drawdown_pct=trough.drawdown_pct,
                    duration_bars=trough_index - peak_index,
                    recovery_bars=None,
                )
            )

        return periods

    @property
    def maximum_drawdown(self) -> float:
        periods = self.periods()

        if not periods:
            return 0.0

        return min(period.drawdown for period in periods)

    @property
    def maximum_drawdown_pct(self) -> float:
        periods = self.periods()

        if not periods:
            return 0.0

        return min(period.drawdown_pct for period in periods)

    @property
    def longest_drawdown_bars(self) -> int:
        periods = self.periods()

        if not periods:
            return 0

        return max(period.duration_bars for period in periods)

    @property
    def longest_recovery_bars(self) -> int | None:
        periods = self.periods()

        recovered = [
            period.recovery_bars
            for period in periods
            if period.recovery_bars is not None
        ]

        if not recovered:
            return None

        return max(recovered)
