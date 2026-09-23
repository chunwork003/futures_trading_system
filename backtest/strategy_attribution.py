from __future__ import annotations

from pydantic import BaseModel, Field

from backtest.models import Direction


class StrategyAttribution(BaseModel):
    strategy_id: str
    symbol: str
    contract: str | None = None
    direction: Direction
    quantity: int = Field(gt=0)
