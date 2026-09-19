from __future__ import annotations

import polars as pl


REQUIRED_COLUMNS = {
    "open",
    "high",
    "low",
    "close",
}


def validate_ohlc_columns(df: pl.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required OHLC columns: "
            f"{sorted(missing)}"
        )


def add_price_features(df: pl.DataFrame) -> pl.DataFrame:
    validate_ohlc_columns(df)

    return df.with_columns(
        [
            (pl.col("high") - pl.col("low"))
            .alias("bar_range"),

            (pl.col("close") - pl.col("open"))
            .alias("body"),

            (pl.col("close") - pl.col("open"))
            .abs()
            .alias("body_abs"),

            (
                pl.col("high")
                - pl.max_horizontal(
                    pl.col("open"),
                    pl.col("close"),
                )
            ).alias("upper_wick"),

            (
                pl.min_horizontal(
                    pl.col("open"),
                    pl.col("close"),
                )
                - pl.col("low")
            ).alias("lower_wick"),

            (
                pl.col("close")
                - pl.col("close").shift(1)
            ).alias("return_points"),

            (
                (
                    pl.col("close")
                    / pl.col("close").shift(1)
                )
                - 1.0
            ).alias("return_pct"),
        ]
    )