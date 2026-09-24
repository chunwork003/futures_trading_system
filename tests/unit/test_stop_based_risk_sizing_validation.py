import pytest

from backtest.stop_based_risk_sizing import StopBasedRiskSizing


@pytest.mark.parametrize("risk_amount", [0, -1, -20_000])
def test_stop_based_risk_rejects_non_positive_risk_amount(risk_amount):
    with pytest.raises(ValueError):
        StopBasedRiskSizing(risk_amount=risk_amount)
