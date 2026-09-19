from datetime import date
from typing import Optional

from pydantic import BaseModel


class Contract(BaseModel):
    contract_id: int
    instrument_id: int

    contract_code: str
    contract_month: date

    listing_date: Optional[date] = None
    last_trade_date: Optional[date] = None
    settlement_date: Optional[date] = None

    status: str = "ACTIVE"