from __future__ import annotations

from pydantic import BaseModel, Field


class SizingComparisonResult(BaseModel):
    strategy_name: str
    total_trades: int = Field(ge=0)
    net_pnl: float
    max_drawdown: float
    final_equity: float = Field(gt=0)
