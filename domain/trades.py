from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Trade(BaseModel):
    trade_id: int

    symbol: str
    contract: str

    entry_time: datetime
    entry_price: float
    entry_side: str
    entry_quantity: int

    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None

    gross_pnl: Optional[float] = None
    commission: float = 0.0
    slippage: float = 0.0
    net_pnl: Optional[float] = None

    exit_reason: Optional[str] = None