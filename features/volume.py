import polars as pl


def add_volume_average(
    df: pl.DataFrame,
    period: int = 20,
) -> pl.DataFrame:

    return df.with_columns(
        pl.col("volume")
        .rolling_mean(period)
        .alias(f"volume_ma_{period}")
    )