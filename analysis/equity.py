from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


@dataclass(frozen=True)
class EquitySnapshot:
    timestamp: datetime
    equity: float
    realized_pnl: float
    unrealized_pnl: float
    peak_equity: float
    drawdown: float
    drawdown_pct: float


class EquityCurve:
    """Equity curve and drawdown calculation."""

    def __init__(self) -> None:
        self.snapshots: list[EquitySnapshot] = []

    def reset(self) -> None:
        self.snapshots = []

    def add_snapshot(
        self,
        *,
        timestamp: datetime,
        equity: float,
        realized_pnl: float,
        unrealized_pnl: float,
    ) -> EquitySnapshot:
        equity = float(equity)
        realized_pnl = float(realized_pnl)
        unrealized_pnl = float(unrealized_pnl)

        if self.snapshots:
            peak_equity = max(self.snapshots[-1].peak_equity, equity)
        else:
            peak_equity = equity

        drawdown = equity - peak_equity
        drawdown_pct = (
            drawdown / peak_equity
            if peak_equity > 0
            else 0.0
        )

        snapshot = EquitySnapshot(
            timestamp=timestamp,
            equity=equity,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            peak_equity=peak_equity,
            drawdown=drawdown,
            drawdown_pct=drawdown_pct,
        )

        self.snapshots.append(snapshot)
        return snapshot

    @property
    def final_equity(self) -> float | None:
        if not self.snapshots:
            return None
        return self.snapshots[-1].equity

    @property
    def max_drawdown(self) -> float:
        if not self.snapshots:
            return 0.0
        return min(snapshot.drawdown for snapshot in self.snapshots)

    @property
    def max_drawdown_pct(self) -> float:
        if not self.snapshots:
            return 0.0
        return min(snapshot.drawdown_pct for snapshot in self.snapshots)

    @classmethod
    def from_snapshots(
        cls,
        snapshots: Iterable[tuple[datetime, float, float, float]],
    ) -> "EquityCurve":
        curve = cls()

        for timestamp, equity, realized_pnl, unrealized_pnl in snapshots:
            curve.add_snapshot(
                timestamp=timestamp,
                equity=equity,
                realized_pnl=realized_pnl,
                unrealized_pnl=unrealized_pnl,
            )

        return curve
