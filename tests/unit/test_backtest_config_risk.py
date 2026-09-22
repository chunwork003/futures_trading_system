from backtest.models import BacktestConfig
from backtest.risk import RiskConfig


def test_backtest_config_accepts_risk_config():
    config = BacktestConfig(
        symbol="TX",
        risk_config=RiskConfig(
            initial_margin_per_contract=50_000,
            maintenance_margin_per_contract=40_000,
            max_contracts=2,
            max_margin_utilization=0.8,
        ),
    )

    assert config.risk_config is not None
    assert config.risk_config.initial_margin_per_contract == 50_000
    assert config.risk_config.maintenance_margin_per_contract == 40_000
    assert config.risk_config.max_contracts == 2
    assert config.risk_config.max_margin_utilization == 0.8


def test_backtest_config_risk_config_defaults_to_none():
    config = BacktestConfig(symbol="TX")

    assert config.risk_config is None
