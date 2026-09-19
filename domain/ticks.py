from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class Tick(BaseModel):
    timestamp: datetime
    trade_date: date

    symbol: str
    contract: Optional[str] = None

    price: float
    volume: int

    bid_price: Optional[float] = None
    ask_price: Optional[float] = None

    bid_volume: Optional[int] = None
    ask_volume: Optional[int] = None

    trade_type: Optional[int] = None

    session: Optional[str] = None

    source: Optional[str] = None