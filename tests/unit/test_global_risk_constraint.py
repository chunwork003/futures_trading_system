from backtest.global_risk_constraint import GlobalRiskConstraint
from backtest.models import Direction
from backtest.risk import PortfolioRiskManager, RiskConfig
from backtest.target_position import TargetAccountPosition


def make_constraint() -> GlobalRiskConstraint:
    return GlobalRiskConstraint(
        PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=80_000,
                maintenance_margin_per_contract=60_000,
                max_contracts=2,
                max_margin_utilization=1.0,
            )
        )
    )


def make_target(quantity: int) -> TargetAccountPosition:
    return TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=quantity,
    )


def test_global_risk_constraint_allows_valid_target():
    constraint = make_constraint()

    assert constraint.allows(
        equity=1_000_000,
        target=make_target(2),
    )


def test_global_risk_constraint_rejects_target_above_max_contracts():
    constraint = make_constraint()

    assert not constraint.allows(
        equity=1_000_000,
        target=make_target(3),
    )
def test_global_risk_constraint_rejects_excessive_margin_utilization():
    constraint = GlobalRiskConstraint(
        PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=80_000,
                maintenance_margin_per_contract=60_000,
                max_contracts=2,
                max_margin_utilization=0.5,
            )
        )
    )

    assert not constraint.allows(
        equity=100_000,
        target=make_target(1),
    )
from backtest.account_position import AccountPosition
from backtest.global_risk_constraint import GlobalRiskConstraint
from backtest.models import Direction
from backtest.risk import PortfolioRiskManager, RiskConfig
from backtest.target_position import TargetAccountPosition


def test_global_risk_constraint_allows_reduce_target():
    constraint = GlobalRiskConstraint(
        PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=80_000,
                maintenance_margin_per_contract=60_000,
                max_contracts=2,
                max_margin_utilization=0.5,
            )
        )
    )

    current = AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=5,
    )

    target = TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=2,
    )

    assert current.quantity > target.quantity
    assert constraint.allows(
        equity=1_000_000,
        target=target,
    )
from backtest.account_position import AccountPosition
from backtest.global_risk_constraint import GlobalRiskConstraint
from backtest.models import Direction
from backtest.risk import PortfolioRiskManager, RiskConfig


def test_global_risk_constraint_allows_exit():
    constraint = GlobalRiskConstraint(
        PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=80_000,
                maintenance_margin_per_contract=60_000,
                max_contracts=1,
                max_margin_utilization=0.1,
            )
        )
    )

    current = AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=5,
    )

    assert current.quantity > constraint.risk_manager.config.max_contracts

    assert constraint.allows(
        equity=1_000_000,
        target=None,
    )
def test_global_risk_constraint_allows_reduce_from_over_limit_position():
    constraint = GlobalRiskConstraint(
        PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=80_000,
                maintenance_margin_per_contract=60_000,
                max_contracts=2,
                max_margin_utilization=0.5,
            )
        )
    )

    current = AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=5,
    )

    target = TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=2,
    )

    assert current.quantity > constraint.risk_manager.config.max_contracts
    assert target.quantity == constraint.risk_manager.config.max_contracts

    assert constraint.allows(
        equity=1_000_000,
        target=target,
    )
def test_global_risk_constraint_allows_hold_at_limit():
    constraint = GlobalRiskConstraint(
        PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=80_000,
                maintenance_margin_per_contract=60_000,
                max_contracts=2,
                max_margin_utilization=0.5,
            )
        )
    )

    current = AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=2,
    )

    target = TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=2,
    )

    assert current.quantity == target.quantity
    assert constraint.allows(
        equity=1_000_000,
        target=target,
    )
def test_global_risk_constraint_allows_add_up_to_limit():
    constraint = GlobalRiskConstraint(
        PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=80_000,
                maintenance_margin_per_contract=60_000,
                max_contracts=2,
                max_margin_utilization=0.5,
            )
        )
    )

    current = AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=1,
    )

    target = TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=2,
    )

    assert target.quantity > current.quantity
    assert constraint.allows(
        equity=1_000_000,
        target=target,
    )


def test_global_risk_constraint_rejects_add_beyond_limit():
    constraint = GlobalRiskConstraint(
        PortfolioRiskManager(
            RiskConfig(
                initial_margin_per_contract=80_000,
                maintenance_margin_per_contract=60_000,
                max_contracts=2,
                max_margin_utilization=0.5,
            )
        )
    )

    current = AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=1,
    )

    target = TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=3,
    )

    assert target.quantity > current.quantity
    assert not constraint.allows(
        equity=1_000_000,
        target=target,
    )
