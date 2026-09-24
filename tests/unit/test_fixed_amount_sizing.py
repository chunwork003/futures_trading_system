from backtest.fixed_amount_sizing import FixedAmountSizing
from backtest.position_sizing import PositionSizingInput


def test_fixed_amount_calculates_quantity_from_price_and_multiplier():
    strategy = FixedAmountSizing(amount=100_000)

    sizing_input = PositionSizingInput(
        equity=1_000_000,
        price=20_000,
        stop_price=19_900,
        multiplier=200,
        risk_budget=0.01,
    )

    assert strategy.calculate(sizing_input) == 0
