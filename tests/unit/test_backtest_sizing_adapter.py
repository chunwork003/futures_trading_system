from backtest.backtest_sizing_adapter import BacktestSizingAdapter
from backtest.fixed_quantity_sizing import FixedQuantitySizing
from backtest.position_sizing import PositionSizingInput


def test_backtest_sizing_adapter_calculates_quantity():
    adapter = BacktestSizingAdapter(
        FixedQuantitySizing(quantity=3)
    )

    sizing_input = PositionSizingInput(
        equity=1_000_000,
        price=20_000,
        stop_price=19_900,
        multiplier=200,
        risk_budget=0.01,
    )

    assert adapter.calculate_quantity(sizing_input) == 3
