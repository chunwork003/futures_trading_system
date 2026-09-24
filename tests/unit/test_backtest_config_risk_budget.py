from backtest.models import BacktestConfig


def test_backtest_config_has_risk_budget():
    config = BacktestConfig(
        symbol="TXF",
        risk_budget=0.02,
    )

    assert config.risk_budget == 0.02


def test_backtest_config_default_risk_budget():
    config = BacktestConfig(
        symbol="TXF",
    )

    assert config.risk_budget == 0.01
