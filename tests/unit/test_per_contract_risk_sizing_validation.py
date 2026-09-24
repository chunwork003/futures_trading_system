import pytest

from backtest.per_contract_risk_sizing import PerContractRiskSizing


@pytest.mark.parametrize("risk_per_contract", [0, -1, -20_000])
def test_per_contract_risk_rejects_non_positive_risk(risk_per_contract):
    with pytest.raises(ValueError):
        PerContractRiskSizing(risk_per_contract=risk_per_contract)
