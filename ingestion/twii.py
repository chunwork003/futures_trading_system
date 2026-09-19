import polars as pl

from .base import DataSource


class TWIIDataSource(DataSource):

    def download(self, start_date, end_date) -> pl.DataFrame:
        raise NotImplementedError(
            "TWII data source has not been implemented."
        )