import polars as pl


class TickCleaner:

    @staticmethod
    def clean(df: pl.DataFrame) -> pl.DataFrame:

        df = df.unique(
            subset=[
                "timestamp",
                "symbol",
                "contract",
                "price",
                "volume",
            ],
            keep="last",
        )

        df = df.filter(
            pl.col("price") > 0
        )

        df = df.filter(
            pl.col("volume") >= 0
        )

        return df.sort(
            [
                "symbol",
                "contract",
                "timestamp",
            ]
        )