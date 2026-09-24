from __future__ import annotations

from backtest.fixed_amount_sizing import FixedAmountSizing
from backtest.fixed_quantity_sizing import FixedQuantitySizing
from backtest.fixed_risk_sizing import FixedRiskSizing
from backtest.per_contract_risk_sizing import PerContractRiskSizing
from backtest.position_sizing_registry import PositionSizingRegistry
from backtest.stop_based_risk_sizing import StopBasedRiskSizing


def build_default_position_sizing_registry() -> PositionSizingRegistry:
    registry = PositionSizingRegistry()

    registry.register(
        "fixed_quantity",
        FixedQuantitySizing(quantity=1),
    )

    registry.register(
        "fixed_amount",
        FixedAmountSizing(amount=1_000_000),
    )

    registry.register(
        "fixed_risk",
        FixedRiskSizing(),
    )

    registry.register(
        "stop_based_risk",
        StopBasedRiskSizing(risk_amount=10_000),
    )

    registry.register(
        "per_contract_risk",
        PerContractRiskSizing(risk_per_contract=10_000),
    )

    return registry
