from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True)
class MarketBar:
    timestamp: datetime
    trade_date: date
    symbol: str
    close: float
    data: dict[str, Any] = field(default_factory=dict)
