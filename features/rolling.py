from __future__ import annotations

import polars as pl


def rolling_high(
    bars: pl.DataFrame,
    window: int,
    source: str = "high",
    output: str | None = None,
) -> pl.DataFrame:
    if window <= 0:
        raise ValueError("window must be positive")

    output = output or f"rolling_high_{window}"

    return bars.with_columns(
        pl.col(source)
        .rolling_max(window_size=window)
        .alias(output)
    )


def rolling_low(
    bars: pl.DataFrame,
    window: int,
    source: str = "low",
    output: str | None = None,
) -> pl.DataFrame:
    if window <= 0:
        raise ValueError("window must be positive")

    output = output or f"rolling_low_{window}"

    return bars.with_columns(
        pl.col(source)
        .rolling_min(window_size=window)
        .alias(output)
    )


def rolling_mean(
    bars: pl.DataFrame,
    window: int,
    source: str = "close",
    output: str | None = None,
) -> pl.DataFrame:
    if window <= 0:
        raise ValueError("window must be positive")

    output = output or f"sma_{window}"

    return bars.with_columns(
        pl.col(source)
        .rolling_mean(window_size=window)
        .alias(output)
    )


def ema(
    bars: pl.DataFrame,
    window: int,
    source: str = "close",
    output: str | None = None,
) -> pl.DataFrame:
    if window <= 0:
        raise ValueError("window must be positive")

    output = output or f"ema_{window}"

    return bars.with_columns(
        pl.col(source)
        .ewm_mean(
            span=window,
            adjust=False,
            min_samples=window,
        )
        .alias(output)
    )
