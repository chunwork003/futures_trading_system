from backtest.fixed_risk_sizing import FixedRiskSizing
from backtest.position_sizing import PositionSizingInput


def test_fixed_risk_calculates_quantity_from_risk_budget():
    strategy = FixedRiskSizing()

    sizing_input = PositionSizingInput(
        equity=1_000_000,
        price=20_000,
        stop_price=19_000,
        multiplier=200,
        risk_budget=0.01,
    )

    assert strategy.calculate(sizing_input) == 0
