from abc import ABC, abstractmethod
from datetime import date

import polars as pl


class DataSource(ABC):
    """Unified interface for all market-data sources."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Stable source identifier."""
        raise NotImplementedError

    @abstractmethod
    def download(
        self,
        start_date: date,
        end_date: date,
        symbol: str = "TXF",
    ) -> pl.DataFrame:
        """Return normalized market data for the requested period."""
        raise NotImplementedError
