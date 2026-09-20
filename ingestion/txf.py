import polars as pl

from .base import DataSource


class TXFDataSource(DataSource):
    """TXF market-data source base implementation."""

    @property
    def source_name(self) -> str:
        return "txf"

    def download(
        self,
        start_date,
        end_date,
        symbol: str = "TXF",
    ) -> pl.DataFrame:
        raise NotImplementedError(
            "TXF data source has not been implemented."
        )
