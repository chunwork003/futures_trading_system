from pathlib import Path

import polars as pl


class ParquetStore:

    def __init__(
        self,
        base_path: str = "data/parquet",
    ):
        self.base_path = Path(base_path)

    def write(
        self,
        df: pl.DataFrame,
        dataset: str,
        symbol: str,
        year: int,
        month: int,
        day: int,
    ) -> Path:

        path = (
            self.base_path
            / dataset
            / symbol
            / f"year={year}"
            / f"month={month:02d}"
        )

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = (
            path
            / f"{symbol}_{year}{month:02d}{day:02d}.parquet"
        )

        df.write_parquet(
            file_path,
            compression="zstd",
        )

        return file_path

    def scan(
        self,
        dataset: str,
        symbol: str,
    ) -> pl.LazyFrame:

        path = (
            self.base_path
            / dataset
            / symbol
            / "**/*.parquet"
        )

        return pl.scan_parquet(
            str(path),
            hive_partitioning=True,
        )