from backtest.risk import (
    PortfolioRiskManager,
    RiskConfig,
)


def make_risk_manager() -> PortfolioRiskManager:
    return PortfolioRiskManager(
        RiskConfig(
            initial_margin_per_contract=80_000,
            maintenance_margin_per_contract=60_000,
            max_contracts=2,
            max_margin_utilization=1.0,
        )
    )


def test_initial_margin_required():
    manager = make_risk_manager()

    assert manager.initial_margin_required(1) == 80_000
    assert manager.initial_margin_required(2) == 160_000


def test_maintenance_margin_required():
    manager = make_risk_manager()

    assert manager.maintenance_margin_required(1) == 60_000
    assert manager.maintenance_margin_required(2) == 120_000


def test_available_capital():
    manager = make_risk_manager()

    assert manager.available_capital(
        equity=1_000_000,
        quantity=1,
    ) == 920_000


def test_margin_utilization():
    manager = make_risk_manager()

    assert manager.margin_utilization(
        equity=1_000_000,
        quantity=1,
    ) == 0.08


def test_can_open_respects_max_contracts():
    manager = make_risk_manager()

    assert manager.can_open(
        equity=1_000_000,
        quantity=2,
    )

    assert not manager.can_open(
        equity=1_000_000,
        quantity=3,
    )


def test_can_open_rejects_insufficient_margin():
    manager = make_risk_manager()

    assert manager.can_open(
        equity=80_000,
        quantity=1,
    )

    assert not manager.can_open(
        equity=79_999,
        quantity=1,
    )


def test_zero_margin_mode_preserves_existing_behavior():
    manager = PortfolioRiskManager(
        RiskConfig(
            initial_margin_per_contract=0,
            maintenance_margin_per_contract=0,
            max_contracts=1,
        )
    )

    assert manager.can_open(
        equity=1,
        quantity=1,
    )

    assert not manager.should_force_liquidate(
        equity=0,
        quantity=1,
    )


def test_force_liquidation_uses_maintenance_margin():
    manager = make_risk_manager()

    assert not manager.should_force_liquidate(
        equity=60_000,
        quantity=1,
    )

    assert manager.should_force_liquidate(
        equity=59_999,
        quantity=1,
    )


def test_position_exposure():
    manager = make_risk_manager()

    assert manager.position_exposure(
        price=25_000,
        quantity=1,
        multiplier=200,
    ) == 5_000_000


def test_snapshot():
    manager = make_risk_manager()

    state = manager.snapshot(
        equity=1_000_000,
        quantity=1,
        price=25_000,
        multiplier=200,
    )

    assert state.equity == 1_000_000
    assert state.quantity == 1
    assert state.initial_margin == 80_000
    assert state.maintenance_margin == 60_000
    assert state.available_capital == 920_000
    assert state.margin_utilization == 0.08
    assert state.position_exposure == 5_000_000


def test_invalid_margin_configuration():
    try:
        RiskConfig(
            initial_margin_per_contract=50_000,
            maintenance_margin_per_contract=60_000,
        )
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for invalid margin configuration"
    )


def test_invalid_quantity():
    manager = make_risk_manager()

    try:
        manager.initial_margin_required(-1)
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for negative quantity"
    )
