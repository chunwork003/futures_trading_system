from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from backtest.models import Direction, PositionStatus


class StrategyVirtualPosition(BaseModel):
    strategy_id: str
    symbol: str
    contract: str | None = None
    direction: Direction
    status: PositionStatus
    quantity: int = Field(gt=0)
    priority: int = Field(default=0)

    @model_validator(mode="after")
    def validate_direction_status(self) -> "StrategyVirtualPosition":
        expected_status = {
            Direction.LONG: PositionStatus.LONG,
            Direction.SHORT: PositionStatus.SHORT,
        }[self.direction]

        if self.status != expected_status:
            raise ValueError(
                "direction and status must represent the same position direction"
            )
        return self
