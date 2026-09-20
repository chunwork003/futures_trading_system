from __future__ import annotations

import polars as pl


def true_range(
    bars: pl.DataFrame,
    output: str = "true_range",
) -> pl.DataFrame:
    required = {"high", "low", "close"}
    missing = required - set(bars.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    return bars.with_columns(
        pl.max_horizontal(
            [
                pl.col("high") - pl.col("low"),
                (pl.col("high") - pl.col("close").shift(1)).abs(),
                (pl.col("low") - pl.col("close").shift(1)).abs(),
            ]
        ).alias(output)
    )


def atr(
    bars: pl.DataFrame,
    window: int = 14,
    output: str | None = None,
) -> pl.DataFrame:
    if window <= 0:
        raise ValueError("window must be positive")

    output = output or f"atr_{window}"

    result = true_range(bars)

    return result.with_columns(
        pl.col("true_range")
        .rolling_mean(window_size=window)
        .alias(output)
    )


def returns(
    bars: pl.DataFrame,
    periods: int = 1,
    source: str = "close",
    output: str | None = None,
) -> pl.DataFrame:
    if periods <= 0:
        raise ValueError("periods must be positive")

    output = output or f"return_{periods}"

    return bars.with_columns(
        (
            pl.col(source) / pl.col(source).shift(periods) - 1.0
        ).alias(output)
    )


def rolling_volatility(
    bars: pl.DataFrame,
    window: int = 20,
    source: str = "close",
    output: str | None = None,
) -> pl.DataFrame:
    if window <= 0:
        raise ValueError("window must be positive")

    output = output or f"volatility_{window}"

    return bars.with_columns(
        pl.col(source)
        .pct_change()
        .rolling_std(window_size=window)
        .alias(output)
    )
