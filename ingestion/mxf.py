import polars as pl

from .base import DataSource


class MXFDataSource(DataSource):
    """MXF market-data source base implementation."""

    @property
    def source_name(self) -> str:
        return "mxf"

    def download(
        self,
        start_date,
        end_date,
        symbol: str = "MXF",
    ) -> pl.DataFrame:
        raise NotImplementedError(
            "MXF data source has not been implemented."
        )
