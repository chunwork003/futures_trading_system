from backtest.default_capital_position_management_registry import (
    build_default_capital_position_management_registry,
)


def test_default_capital_position_management_registry_contains_fixed_ratio():
    registry = build_default_capital_position_management_registry()

    assert registry.names() == ("fixed_ratio",)


def test_default_capital_position_management_registry_returns_fixed_ratio():
    registry = build_default_capital_position_management_registry()

    strategy = registry.get("fixed_ratio")

    assert strategy is not None
