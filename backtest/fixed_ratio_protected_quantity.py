from __future__ import annotations

from math import floor

from backtest.fixed_ratio_risk_multiplier import get_risk_multiplier
from backtest.fixed_ratio_risk_level import FixedRatioRiskLevel
from backtest.fixed_ratio_risk_multipliers import FixedRatioRiskMultipliers


def calculate_protected_quantity(
    base_quantity: int,
    level: FixedRatioRiskLevel,
    multipliers: FixedRatioRiskMultipliers,
) -> int:
    if base_quantity < 0:
        raise ValueError("base_quantity must not be negative")

    multiplier = get_risk_multiplier(
        level,
        multipliers,
    )

    return floor(base_quantity * multiplier)
