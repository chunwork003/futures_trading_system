import polars as pl


def add_moving_average(
    df: pl.DataFrame,
    periods=(5, 20, 60),
) -> pl.DataFrame:

    expressions = []

    for period in periods:
        expressions.append(
            pl.col("close")
            .rolling_mean(period)
            .alias(f"ma_{period}")
        )

    return df.with_columns(expressions)