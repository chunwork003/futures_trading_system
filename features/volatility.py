import polars as pl


def add_true_range(df: pl.DataFrame) -> pl.DataFrame:

    return df.with_columns(
        pl.max_horizontal(
            [
                pl.col("high") - pl.col("low"),
                (
                    pl.col("high")
                    - pl.col("close").shift(1)
                ).abs(),
                (
                    pl.col("low")
                    - pl.col("close").shift(1)
                ).abs(),
            ]
        ).alias("true_range")
    )