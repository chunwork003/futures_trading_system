from backtest.capital_position_management_registry import (
    CapitalPositionManagementRegistry,
)
from backtest.fixed_ratio_capital_position_strategy import (
    FixedRatioCapitalPositionStrategy,
)
from backtest.fixed_ratio_parameters import FixedRatioParameters


def build_default_capital_position_management_registry() -> (
    CapitalPositionManagementRegistry
):
    registry = CapitalPositionManagementRegistry()

    registry.register(
        "fixed_ratio",
        FixedRatioCapitalPositionStrategy(
            FixedRatioParameters(
                initial_equity=1_000_000,
                delta=100_000,
                base_quantity=1,
            )
        ),
    )

    return registry
