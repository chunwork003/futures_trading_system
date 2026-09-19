from __future__ import annotations

import polars as pl

from features.price import validate_ohlc_columns


def add_trend_features(df: pl.DataFrame) -> pl.DataFrame:
    validate_ohlc_columns(df)

    return df.with_columns(
        [
            pl.col("close")
            .rolling_mean(window_size=5)
            .alias("sma_5"),

            pl.col("close")
            .rolling_mean(window_size=20)
            .alias("sma_20"),

            pl.col("close")
            .rolling_mean(window_size=60)
            .alias("sma_60"),

            pl.col("close")
            .ewm_mean(
                span=20,
                adjust=False,
                min_samples=20,
            )
            .alias("ema_20"),

            pl.col("close")
            .ewm_mean(
                span=60,
                adjust=False,
                min_samples=60,
            )
            .alias("ema_60"),
        ]
    ).with_columns(
        [
            (
                pl.col("close")
                - pl.col("sma_20")
            ).alias("close_vs_sma20"),

            (
                (
                    pl.col("close")
                    / pl.col("sma_20")
                )
                - 1.0
            ).alias("close_vs_sma20_pct"),

            (
                pl.col("sma_20")
                - pl.col("sma_20").shift(1)
            ).alias("sma20_slope"),

            (
                pl.col("sma_20")
                - pl.col("sma_20").shift(5)
            ).alias("sma20_slope_5"),
        ]
    )
