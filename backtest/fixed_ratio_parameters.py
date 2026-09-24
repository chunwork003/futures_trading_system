from __future__ import annotations

from pydantic import BaseModel, Field


class FixedRatioParameters(BaseModel):
    initial_equity: float = Field(gt=0)
    delta: float = Field(gt=0)
    base_quantity: int = Field(gt=0)
