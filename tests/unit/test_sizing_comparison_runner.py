from backtest.fixed_quantity_sizing import FixedQuantitySizing
from backtest.fixed_risk_sizing import FixedRiskSizing
from backtest.sizing_comparison_runner import SizingComparisonRunner


def test_sizing_comparison_runner_keeps_strategies():
    fixed_quantity = FixedQuantitySizing(quantity=1)
    fixed_risk = FixedRiskSizing()

    runner = SizingComparisonRunner(
        strategies={
            "fixed_quantity": fixed_quantity,
            "fixed_risk": fixed_risk,
        }
    )

    assert runner.strategies["fixed_quantity"] is fixed_quantity
    assert runner.strategies["fixed_risk"] is fixed_risk


def test_sizing_comparison_runner_rejects_empty_strategies():
    try:
        SizingComparisonRunner({})
    except ValueError as exc:
        assert str(exc) == "at least one sizing strategy is required"
    else:
        raise AssertionError("expected ValueError")
