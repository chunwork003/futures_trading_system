from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

class PositionSizingInput(BaseModel):
    equity: float = Field(gt=0)
    price: float = Field(gt=0)
    stop_price: float = Field(gt=0)
    multiplier: float = Field(gt=0)
    risk_budget: float = Field(gt=0, le=1)


class PositionSizingStrategy(ABC):
    @abstractmethod
    def calculate(
        self,
        sizing_input: PositionSizingInput,
    ) -> int:
        raise NotImplementedError
