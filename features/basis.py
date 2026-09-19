import polars as pl


def add_basis(
    df: pl.DataFrame,
    index_column: str = "twii_close",
) -> pl.DataFrame:

    return df.with_columns(
        (
            pl.col("close")
            - pl.col(index_column)
        ).alias("basis")
    )