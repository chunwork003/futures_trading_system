import polars as pl

from .base import DataSource


class TWIIDataSource(DataSource):
    """TWII market-data source base implementation."""

    @property
    def source_name(self) -> str:
        return "twii"

    def download(
        self,
        start_date,
        end_date,
        symbol: str = "TWII",
    ) -> pl.DataFrame:
        raise NotImplementedError(
            "TWII data source has not been implemented."
        )
