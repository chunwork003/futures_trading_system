from backtest.position_sizing import PositionSizingInput
from backtest.per_contract_risk_sizing import PerContractRiskSizing


def test_per_contract_risk_returns_zero_when_risk_budget_cannot_cover_one_contract():
    strategy = PerContractRiskSizing(risk_per_contract=20_000)

    sizing_input = PositionSizingInput(
        equity=1_000_000,
        price=20_000,
        stop_price=19_900,
        multiplier=200,
        risk_budget=0.01,
    )

    assert strategy.calculate(sizing_input) == 0
