from backtest.position_sizing import PositionSizingInput
from backtest.stop_based_risk_sizing import StopBasedRiskSizing


def test_stop_based_risk_calculates_quantity_from_stop_distance():
    strategy = StopBasedRiskSizing(risk_amount=20_000)

    sizing_input = PositionSizingInput(
        equity=1_000_000,
        price=20_000,
        stop_price=19_900,
        multiplier=200,
        risk_budget=0.01,
    )

    assert strategy.calculate(sizing_input) == 1


def test_stop_based_risk_uses_absolute_stop_distance():
    strategy = StopBasedRiskSizing(risk_amount=40_000)

    sizing_input = PositionSizingInput(
        equity=1_000_000,
        price=19_900,
        stop_price=20_000,
        multiplier=200,
        risk_budget=0.01,
    )

    assert strategy.calculate(sizing_input) == 2
