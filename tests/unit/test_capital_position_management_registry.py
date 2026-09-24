import pytest

from backtest.capital_position_management_registry import (
    CapitalPositionManagementRegistry,
)
from backtest.fixed_ratio_capital_position_strategy import (
    FixedRatioCapitalPositionStrategy,
)
from backtest.fixed_ratio_parameters import FixedRatioParameters


def make_strategy() -> FixedRatioCapitalPositionStrategy:
    return FixedRatioCapitalPositionStrategy(
        FixedRatioParameters(
            initial_equity=1_000_000,
            delta=100_000,
            base_quantity=1,
        )
    )


def test_capital_position_management_registry_register_and_get():
    registry = CapitalPositionManagementRegistry()
    strategy = make_strategy()

    registry.register("fixed_ratio", strategy)

    assert registry.get("fixed_ratio") is strategy


def test_capital_position_management_registry_lists_names():
    registry = CapitalPositionManagementRegistry()

    registry.register(
        "fixed_ratio",
        make_strategy(),
    )

    assert registry.names() == ("fixed_ratio",)


def test_capital_position_management_registry_rejects_duplicate_name():
    registry = CapitalPositionManagementRegistry()

    registry.register(
        "fixed_ratio",
        make_strategy(),
    )

    with pytest.raises(ValueError):
        registry.register(
            "fixed_ratio",
            make_strategy(),
        )


def test_capital_position_management_registry_rejects_empty_name():
    registry = CapitalPositionManagementRegistry()

    with pytest.raises(ValueError):
        registry.register(
            "",
            make_strategy(),
        )


def test_capital_position_management_registry_rejects_unknown_strategy():
    registry = CapitalPositionManagementRegistry()

    with pytest.raises(KeyError):
        registry.get("unknown")
