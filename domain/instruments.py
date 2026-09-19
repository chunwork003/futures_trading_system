from pydantic import BaseModel
from typing import Optional


class Instrument(BaseModel):
    instrument_id: int
    symbol: str
    name: str
    asset_type: str
    exchange: str
    currency: str = "TWD"
    multiplier: Optional[float] = None
    tick_size: Optional[float] = None