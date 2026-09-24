from __future__ import annotations

from backtest.backtest_sizing_adapter import BacktestSizingAdapter
from backtest.models import Signal
from backtest.position_sizing import PositionSizingInput


def apply_position_sizing_to_signal(
    signal: Signal,
    adapter: BacktestSizingAdapter,
    sizing_input: PositionSizingInput,
) -> Signal:
    quantity = adapter.calculate_quantity(sizing_input)

    if quantity <= 0:
        raise ValueError(
            "position sizing produced zero quantity"
        )

    return signal.model_copy(
        update={
            "quantity": quantity,
        }
    )
