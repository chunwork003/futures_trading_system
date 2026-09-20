from __future__ import annotations

import polars as pl

from features.price import validate_ohlc_columns


def add_trend_features(df: pl.DataFrame) -> pl.DataFrame:
    """
    Backward-compatible trend feature set.

    Existing project API:
    - sma_5
    - sma_20
    - sma_60
    - ema_20
    - ema_60
    - close_vs_sma20
    - close_vs_sma20_pct
    - sma20_slope
    - sma20_slope_5
    """
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


def trend_features(
    bars: pl.DataFrame,
    fast_window: int = 20,
    slow_window: int = 60,
) -> pl.DataFrame:
    """
    Extended trend-state feature set.

    States:
    - UP
    - DOWN
    - STRENGTHENING
    - WEAKENING
    - SIDEWAYS
    """
    validate_ohlc_columns(bars)

    if fast_window <= 0 or slow_window <= 0:
        raise ValueError("window must be positive")

    if fast_window >= slow_window:
        raise ValueError(
            "fast_window must be smaller than slow_window"
        )

    result = bars.with_columns(
        [
            pl.col("close")
            .ewm_mean(
                span=fast_window,
                adjust=False,
                min_samples=fast_window,
            )
            .alias(f"ema_{fast_window}"),

            pl.col("close")
            .ewm_mean(
                span=slow_window,
                adjust=False,
                min_samples=slow_window,
            )
            .alias(f"ema_{slow_window}"),
        ]
    )

    fast = pl.col(f"ema_{fast_window}")
    slow = pl.col(f"ema_{slow_window}")

    result = result.with_columns(
        [
            (fast - slow).alias("trend_spread"),

            fast.diff().alias(
                f"ema_{fast_window}_slope"
            ),

            slow.diff().alias(
                f"ema_{slow_window}_slope"
            ),
        ]
    )

    return result.with_columns(
        pl.when(
            (fast > slow)
            & (
                pl.col(f"ema_{fast_window}_slope") > 0
            )
        )
        .then(pl.lit("UP"))

        .when(
            (fast < slow)
            & (
                pl.col(f"ema_{fast_window}_slope") < 0
            )
        )
        .then(pl.lit("DOWN"))

        .when(
            (fast > slow)
            & (
                pl.col(f"ema_{fast_window}_slope") <= 0
            )
        )
        .then(pl.lit("WEAKENING"))

        .when(
            (fast < slow)
            & (
                pl.col(f"ema_{fast_window}_slope") >= 0
            )
        )
        .then(pl.lit("STRENGTHENING"))

        .otherwise(pl.lit("SIDEWAYS"))
        .alias("trend_state")
    )
