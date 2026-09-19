import polars as pl


def add_momentum(
    df: pl.DataFrame,
    period: int = 10,
) -> pl.DataFrame:

    return df.with_columns(
        (
            pl.col("close")
            - pl.col("close").shift(period)
        ).alias("momentum")
    )