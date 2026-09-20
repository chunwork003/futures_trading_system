from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StrategyParameters:
    """Immutable parameters shared by strategy implementations."""

    symbol: str
    timeframe: str = "1m"
    quantity: int = 1

    stop_price: Optional[float] = None
    target_price: Optional[float] = None

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol must not be empty")

        if not self.timeframe:
            raise ValueError("timeframe must not be empty")

        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero")

        if self.stop_price is not None and self.stop_price <= 0:
            raise ValueError("stop_price must be greater than zero")

        if self.target_price is not None and self.target_price <= 0:
            raise ValueError("target_price must be greater than zero")
