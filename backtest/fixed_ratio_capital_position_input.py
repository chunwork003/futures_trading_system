from __future__ import annotations

from pydantic import BaseModel, Field

from backtest.fixed_ratio_risk_multipliers import FixedRatioRiskMultipliers
from backtest.fixed_ratio_risk_thresholds import FixedRatioRiskThresholds


class FixedRatioCapitalPositionInput(BaseModel):
    equity: float = Field(gt=0)
    base_quantity: int = Field(gt=0)
    reference_equity: float = Field(gt=0)
    risk_thresholds: FixedRatioRiskThresholds
    risk_multipliers: FixedRatioRiskMultipliers
