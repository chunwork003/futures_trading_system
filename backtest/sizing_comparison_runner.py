from __future__ import annotations

from collections.abc import Iterable, Mapping

from backtest.engine import BacktestEngine
from backtest.models import BacktestConfig, Signal
from backtest.position_sizing import PositionSizingStrategy
from backtest.sizing_comparison import SizingComparisonResult


class SizingComparisonRunner:
    def __init__(
        self,
        strategies: Mapping[str, PositionSizingStrategy],
    ) -> None:
        if not strategies:
            raise ValueError("at least one sizing strategy is required")

        self.strategies = dict(strategies)

    def run(
        self,
        config: BacktestConfig,
        bars: Iterable[dict],
        signals: Iterable[Signal],
    ) -> dict[str, SizingComparisonResult]:
        bars_list = list(bars)
        signals_list = list(signals)

        results: dict[str, SizingComparisonResult] = {}

        for name, strategy in self.strategies.items():
            engine = BacktestEngine(
                config=config,
                position_sizing_strategy=strategy,
            )

            trades = engine.run(
                bars=bars_list,
                signals=signals_list,
            )

            net_pnl = sum(
                trade.net_pnl
                for trade in trades
            )

            final_equity = engine.equity_curve.final_equity

            if final_equity is None:
                final_equity = config.initial_capital

            results[name] = SizingComparisonResult(
                strategy_name=name,
                total_trades=len(trades),
                net_pnl=net_pnl,
                max_drawdown=engine.equity_curve.max_drawdown,
                final_equity=final_equity,
            )

        return results
