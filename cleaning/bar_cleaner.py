import polars as pl


class BarCleaner:

    @staticmethod
    def clean(df: pl.DataFrame) -> pl.DataFrame:

        df = df.unique(
            subset=[
                "timestamp",
                "symbol",
                "contract",
                "timeframe",
            ],
            keep="last",
        )

        df = df.sort(
            [
                "symbol",
                "contract",
                "timestamp",
            ]
        )

        df = df.with_columns(
            pl.col("volume")
            .cast(pl.Int64)
        )

        return df