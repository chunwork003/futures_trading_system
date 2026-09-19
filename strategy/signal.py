import polars as pl


def create_signal_column(
    df: pl.DataFrame,
) -> pl.DataFrame:

    return df.with_columns(
        pl.lit("NONE").alias("signal")
    )