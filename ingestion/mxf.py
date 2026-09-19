import polars as pl

from .base import DataSource


class MXFDataSource(DataSource):

    def download(self, start_date, end_date) -> pl.DataFrame:
        raise NotImplementedError(
            "MXF data source has not been implemented."
        )