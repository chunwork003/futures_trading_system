import pytest

from backtest.fixed_risk_sizing import FixedRiskSizing
from backtest.position_sizing import PositionSizingInput


def test_fixed_risk_rejects_zero_stop_distance():
    strategy = FixedRiskSizing()

    sizing_input = PositionSizingInput(
        equity=1_000_000,
        price=20_000,
        stop_price=20_000,
        multiplier=200,
        risk_budget=0.01,
    )

    with pytest.raises(ValueError):
        strategy.calculate(sizing_input)
