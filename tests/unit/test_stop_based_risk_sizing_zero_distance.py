import pytest

from backtest.position_sizing import PositionSizingInput
from backtest.stop_based_risk_sizing import StopBasedRiskSizing


def test_stop_based_risk_rejects_zero_stop_distance():
    strategy = StopBasedRiskSizing(risk_amount=20_000)

    sizing_input = PositionSizingInput(
        equity=1_000_000,
        price=20_000,
        stop_price=20_000,
        multiplier=200,
        risk_budget=0.01,
    )

    with pytest.raises(ValueError):
        strategy.calculate(sizing_input)
