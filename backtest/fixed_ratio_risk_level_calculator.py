from __future__ import annotations

from backtest.fixed_ratio_risk_level import FixedRatioRiskLevel
from backtest.fixed_ratio_risk_thresholds import FixedRatioRiskThresholds


def determine_fixed_ratio_risk_level(
    drawdown: float,
    thresholds: FixedRatioRiskThresholds,
) -> FixedRatioRiskLevel:
    if drawdown < 0:
        raise ValueError("drawdown must not be negative")

    if drawdown < thresholds.level_1_drawdown:
        return FixedRatioRiskLevel.NORMAL

    if drawdown < thresholds.level_2_drawdown:
        return FixedRatioRiskLevel.LEVEL_1

    if drawdown < thresholds.level_3_drawdown:
        return FixedRatioRiskLevel.LEVEL_2

    return FixedRatioRiskLevel.LEVEL_3
