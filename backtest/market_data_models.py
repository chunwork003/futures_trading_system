from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True)
class MarketBar:
    timestamp: datetime
    trade_date: date
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float | None = None
    tick_count: int | None = None
    timeframe: str | None = None
    exchange: str | None = None
    contract: str | None = None
    session: str | None = None
    source: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
