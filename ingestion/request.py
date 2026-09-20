from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DataRequest:
    """Standardized market-data request."""

    symbol: str
    start_date: date
    end_date: date
    timeframe: str = "1m"

    def __post_init__(self) -> None:
        if self.start_date > self.end_date:
            raise ValueError("start_date must be <= end_date")

        if not self.symbol:
            raise ValueError("symbol must not be empty")

        if not self.timeframe:
            raise ValueError("timeframe must not be empty")
