from backtest.default_position_sizing_registry import (
    build_default_position_sizing_registry,
)


def test_default_position_sizing_registry_contains_all_position_sizing_methods():
    registry = build_default_position_sizing_registry()

    assert registry.names() == (
        "fixed_quantity",
        "fixed_amount",
        "fixed_risk",
        "stop_based_risk",
        "per_contract_risk",
    )


def test_default_position_sizing_registry_returns_registered_strategy():
    registry = build_default_position_sizing_registry()

    strategy = registry.get("fixed_quantity")

    assert strategy.quantity == 1
