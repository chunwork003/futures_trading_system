from backtest.position_sizing import PositionSizingInput
from backtest.fixed_quantity_sizing import FixedQuantitySizing


def test_fixed_quantity_returns_configured_quantity():
    strategy = FixedQuantitySizing(quantity=3)

    sizing_input = PositionSizingInput(
        equity=1_000_000,
        price=20_000,
        stop_price=19_900,
        multiplier=200,
        risk_budget=0.01,
    )

    assert strategy.calculate(sizing_input) == 3
