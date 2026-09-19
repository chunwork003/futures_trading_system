import math

import polars as pl

from features.trend import add_trend_features


def make_bars() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "open": [1.0, 2.0, 3.0, 4.0, 5.0],
            "high": [2.0, 3.0, 4.0, 5.0, 6.0],
            "low": [0.0, 1.0, 2.0, 3.0, 4.0],
            "close": [1.0, 2.0, 3.0, 4.0, 5.0],
        }
    )


def make_long_bars(count: int = 100) -> pl.DataFrame:
    close = [float(value) for value in range(1, count + 1)]

    return pl.DataFrame(
        {
            "open": close,
            "high": [value + 1.0 for value in close],
            "low": [value - 1.0 for value in close],
            "close": close,
        }
    )


def test_sma_features():
    result = add_trend_features(make_bars())

    assert result["sma_5"].to_list() == [
        None,
        None,
        None,
        None,
        3.0,
    ]

    assert result["sma_20"].to_list() == [
        None,
        None,
        None,
        None,
        None,
    ]

    assert result["sma_60"].to_list() == [
        None,
        None,
        None,
        None,
        None,
    ]


def test_sma20_derived_features_are_null_until_available():
    result = add_trend_features(make_bars())

    assert result["close_vs_sma20"].to_list() == [
        None,
        None,
        None,
        None,
        None,
    ]

    assert result["sma20_slope"].to_list() == [
        None,
        None,
        None,
        None,
        None,
    ]


def test_ema_warmup():
    result = add_trend_features(make_long_bars(60))

    ema20 = result["ema_20"].to_list()
    ema60 = result["ema_60"].to_list()

    assert ema20[:19] == [None] * 19
    assert ema20[19] is not None

    assert ema60[:59] == [None] * 59
    assert ema60[59] is not None


def test_ema_values_are_numeric_after_warmup():
    result = add_trend_features(make_long_bars(100))

    ema20 = result["ema_20"].to_list()
    ema60 = result["ema_60"].to_list()

    assert all(value is not None for value in ema20[19:])
    assert all(value is not None for value in ema60[59:])

    assert all(math.isfinite(value) for value in ema20[19:])
    assert all(math.isfinite(value) for value in ema60[59:])


def test_ema_has_no_lookahead():
    full = add_trend_features(make_long_bars(100))
    prefix = add_trend_features(make_long_bars(80))

    full_ema20 = full["ema_20"].to_list()
    prefix_ema20 = prefix["ema_20"].to_list()

    full_ema60 = full["ema_60"].to_list()
    prefix_ema60 = prefix["ema_60"].to_list()

    assert full_ema20[:80] == prefix_ema20
    assert full_ema60[:80] == prefix_ema60
