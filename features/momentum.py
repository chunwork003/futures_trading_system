from __future__ import annotations

import polars as pl


def roc(
    bars: pl.DataFrame,
    window: int = 10,
    source: str = "close",
    output: str | None = None,
) -> pl.DataFrame:
    if window <= 0:
        raise ValueError("window must be positive")

    output = output or f"roc_{window}"

    return bars.with_columns(
        (
            pl.col(source) / pl.col(source).shift(window) - 1.0
        ).alias(output)
    )


def rsi(
    bars: pl.DataFrame,
    window: int = 14,
    source: str = "close",
    output: str | None = None,
) -> pl.DataFrame:
    if window <= 0:
        raise ValueError("window must be positive")

    output = output or f"rsi_{window}"

    delta = pl.col(source).diff()

    gain = (
        pl.when(delta > 0)
        .then(delta)
        .otherwise(0.0)
    )

    loss = (
        pl.when(delta < 0)
        .then(-delta)
        .otherwise(0.0)
    )

    avg_gain = gain.rolling_mean(window_size=window)
    avg_loss = loss.rolling_mean(window_size=window)

    rs = avg_gain / avg_loss

    rsi_expr = (
        pl.when(avg_loss == 0)
        .then(
            pl.when(avg_gain > 0)
            .then(100.0)
            .otherwise(50.0)
        )
        .otherwise(100.0 - (100.0 / (1.0 + rs)))
    )

    return bars.with_columns(
        rsi_expr.alias(output)
    )
