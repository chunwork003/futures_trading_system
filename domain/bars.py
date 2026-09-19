from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class Bar(BaseModel):
    timestamp: datetime
    trade_date: date

    symbol: str
    contract: Optional[str] = None

    timeframe: str

    open: float
    high: float
    low: float
    close: float

    volume: int

    trade_count: Optional[int] = None

    session: Optional[str] = None

    source: Optional[str] = None