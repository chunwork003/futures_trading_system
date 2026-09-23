from __future__ import annotations

from pydantic import BaseModel, Field


class StrategyConflict(BaseModel):
    symbol: str
    contract: str | None = None
    strategy_ids: list[str] = Field(min_length=2)
