from backtest.engine import BacktestEngine
from backtest.models import BacktestConfig
from backtest.risk import PortfolioRiskManager, RiskConfig


def test_engine_creates_default_risk_manager():
    engine = BacktestEngine(
        BacktestConfig(symbol="TX")
    )

    assert isinstance(engine.risk_manager, PortfolioRiskManager)
    assert engine.risk_manager.config == RiskConfig()


def test_engine_uses_configured_risk_manager():
    risk_config = RiskConfig(
        initial_margin_per_contract=50_000,
        maintenance_margin_per_contract=40_000,
        max_contracts=2,
        max_margin_utilization=0.8,
    )

    engine = BacktestEngine(
        BacktestConfig(
            symbol="TX",
            risk_config=risk_config,
        )
    )

    assert engine.risk_manager.config == risk_config
