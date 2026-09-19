from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Signal(BaseModel):
    timestamp: datetime
    symbol: str
    contract: Optional[str] = None

    strategy: str

    signal: str
    direction: Optional[str] = None

    price: Optional[float] = None

    strength: Optional[float] = None

    reason: Optional[str] = None