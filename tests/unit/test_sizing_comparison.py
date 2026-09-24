from backtest.sizing_comparison import SizingComparisonResult


def test_sizing_comparison_result():
    result = SizingComparisonResult(
        strategy_name="fixed_risk",
        total_trades=10,
        net_pnl=25000,
        max_drawdown=-12000,
        final_equity=1025000,
    )

    assert result.strategy_name == "fixed_risk"
    assert result.total_trades == 10
    assert result.net_pnl == 25000
    assert result.max_drawdown == -12000
    assert result.final_equity == 1025000
