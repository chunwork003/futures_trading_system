from __future__ import annotations

from pydantic import BaseModel, Field


class FixedRatioRiskMultipliers(BaseModel):
    normal: float = Field(gt=0, le=1)
    level_1: float = Field(ge=0, le=1)
    level_2: float = Field(ge=0, le=1)
    level_3: float = Field(ge=0, le=1)
