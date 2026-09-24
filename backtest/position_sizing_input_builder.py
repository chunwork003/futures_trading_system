from __future__ import annotations

from backtest.models import BacktestConfig, Signal
from backtest.position_sizing import PositionSizingInput


def build_position_sizing_input(
    config: BacktestConfig,
    signal: Signal,
    equity: float,
) -> PositionSizingInput:
    if signal.stop_price is None:
        raise ValueError(
            "position sizing requires signal.stop_price"
        )

    return PositionSizingInput(
        equity=equity,
        price=signal.entry_price,
        stop_price=signal.stop_price,
        multiplier=config.multiplier,
        risk_budget=config.risk_budget,
    )
