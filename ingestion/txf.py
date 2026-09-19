from abc import ABC, abstractmethod

import polars as pl


class DataSource(ABC):

    @abstractmethod
    def download(self, start_date, end_date) -> pl.DataFrame:
        raise NotImplementedError