from __future__ import annotations

from backtest.fixed_ratio_risk_level import FixedRatioRiskLevel
from backtest.fixed_ratio_risk_multipliers import FixedRatioRiskMultipliers


def get_risk_multiplier(
    level: FixedRatioRiskLevel,
    multipliers: FixedRatioRiskMultipliers,
) -> float:
    mapping = {
        FixedRatioRiskLevel.NORMAL: multipliers.normal,
        FixedRatioRiskLevel.LEVEL_1: multipliers.level_1,
        FixedRatioRiskLevel.LEVEL_2: multipliers.level_2,
        FixedRatioRiskLevel.LEVEL_3: multipliers.level_3,
    }

    return mapping[level]
