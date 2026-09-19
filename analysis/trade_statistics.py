from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from backtest.models import Trade


@dataclass(frozen=True)
class TradeStatistics:
    total_trades: int
    winning_trades: int
    losing_trades: int
    breakeven_trades: int

    win_rate: float

    gross_profit: float
    gross_loss: float
    net_profit: float

    average_trade: float
    average_winner: float
    average_loser: float

    largest_winner: float
    largest_loser: float

    average_holding_minutes: float | None
    average_r_multiple: float | None


class TradeStatisticsAnalyzer:
    """Calculate aggregate statistics from completed trades."""

    def __init__(self, trades: Iterable[Trade]) -> None:
        self.trades = list(trades)

    def calculate(self) -> TradeStatistics:
        trades = self.trades
        total = len(trades)

        if total == 0:
            return TradeStatistics(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                breakeven_trades=0,
                win_rate=0.0,
                gross_profit=0.0,
                gross_loss=0.0,
                net_profit=0.0,
                average_trade=0.0,
                average_winner=0.0,
                average_loser=0.0,
                largest_winner=0.0,
                largest_loser=0.0,
                average_holding_minutes=None,
                average_r_multiple=None,
            )

        net_pnls = [float(trade.net_pnl) for trade in trades]

        winners = [pnl for pnl in net_pnls if pnl > 0]
        losers = [pnl for pnl in net_pnls if pnl < 0]

        holding_times = [
            float(trade.holding_minutes)
            for trade in trades
            if trade.holding_minutes is not None
        ]

        r_multiples = [
            float(trade.r_multiple)
            for trade in trades
            if trade.r_multiple is not None
        ]

        return TradeStatistics(
            total_trades=total,
            winning_trades=len(winners),
            losing_trades=len(losers),
            breakeven_trades=total - len(winners) - len(losers),
            win_rate=len(winners) / total,
            gross_profit=sum(winners),
            gross_loss=sum(losers),
            net_profit=sum(net_pnls),
            average_trade=sum(net_pnls) / total,
            average_winner=sum(winners) / len(winners) if winners else 0.0,
            average_loser=sum(losers) / len(losers) if losers else 0.0,
            largest_winner=max(winners) if winners else 0.0,
            largest_loser=min(losers) if losers else 0.0,
            average_holding_minutes=(
                sum(holding_times) / len(holding_times)
                if holding_times
                else None
            ),
            average_r_multiple=(
                sum(r_multiples) / len(r_multiples)
                if r_multiples
                else None
            ),
        )
