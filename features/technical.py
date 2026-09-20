from __future__ import annotations

import polars as pl

from features.momentum import roc, rsi
from features.rolling import ema, rolling_high, rolling_low, rolling_mean
from features.volatility import atr, returns, rolling_volatility


def add_standard_features(
    bars: pl.DataFrame,
    sma_windows: tuple[int, ...] = (20, 60),
    ema_windows: tuple[int, ...] = (20, 60),
    atr_window: int = 14,
    rsi_window: int = 14,
    roc_window: int = 10,
    volatility_window: int = 20,
) -> pl.DataFrame:
    result = bars

    for window in sma_windows:
        result = rolling_mean(result, window)

    for window in ema_windows:
        result = ema(result, window)

    result = rolling_high(result, 20)
    result = rolling_low(result, 20)

    result = returns(result, 1)
    result = returns(result, 5)

    result = rolling_volatility(
        result,
        window=volatility_window,
    )

    result = atr(
        result,
        window=atr_window,
    )

    result = rsi(
        result,
        window=rsi_window,
    )

    result = roc(
        result,
        window=roc_window,
    )

    return result
