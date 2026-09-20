import math

import polars as pl
import pytest

from features import (
    FeatureRegistry,
    add_standard_features,
    atr,
    ema,
    returns,
    roc,
    rolling_high,
    rolling_low,
    rolling_mean,
    rolling_volatility,
    rsi,
    trend_features,
)


def sample_bars() -> pl.DataFrame:
    close = [
        100.0,
        101.0,
        102.0,
        101.0,
        103.0,
        105.0,
        104.0,
        106.0,
        108.0,
        107.0,
        109.0,
        111.0,
        110.0,
        112.0,
        114.0,
        113.0,
        115.0,
        117.0,
        116.0,
        118.0,
    ]

    return pl.DataFrame(
        {
            "timestamp": list(range(len(close))),
            "open": close,
            "high": [value + 1 for value in close],
            "low": [value - 1 for value in close],
            "close": close,
            "volume": [100] * len(close),
        }
    )


def test_rolling_mean():
    result = rolling_mean(
        sample_bars(),
        window=3,
    )

    assert "sma_3" in result.columns
    assert result["sma_3"][2] == pytest.approx(101.0)


def test_rolling_high():
    result = rolling_high(
        sample_bars(),
        window=3,
    )

    assert result["rolling_high_3"][2] == pytest.approx(103.0)


def test_rolling_low():
    result = rolling_low(
        sample_bars(),
        window=3,
    )

    assert result["rolling_low_3"][2] == pytest.approx(99.0)


def test_ema():
    result = ema(
        sample_bars(),
        window=3,
    )

    assert "ema_3" in result.columns
    assert result["ema_3"].null_count() == 2


def test_returns():
    result = returns(
        sample_bars(),
        periods=1,
    )

    assert result["return_1"][1] == pytest.approx(0.01)


def test_atr():
    result = atr(
        sample_bars(),
        window=3,
    )

    assert "atr_3" in result.columns
    assert result["atr_3"].null_count() >= 1


def test_rolling_volatility():
    result = rolling_volatility(
        sample_bars(),
        window=3,
    )

    assert "volatility_3" in result.columns


def test_rsi():
    result = rsi(
        sample_bars(),
        window=3,
    )

    assert "rsi_3" in result.columns

    valid = result["rsi_3"].drop_nulls()

    assert valid.len() > 0
    assert all(
        0.0 <= value <= 100.0
        for value in valid.to_list()
        if not math.isnan(value)
    )


def test_roc():
    result = roc(
        sample_bars(),
        window=3,
    )

    assert "roc_3" in result.columns
    assert result["roc_3"][3] == pytest.approx(0.01)


def test_trend_features():
    result = trend_features(
        sample_bars(),
        fast_window=3,
        slow_window=5,
    )

    assert "ema_3" in result.columns
    assert "ema_5" in result.columns
    assert "trend_spread" in result.columns
    assert "ema_3_slope" in result.columns
    assert "trend_state" in result.columns


def test_standard_feature_pipeline():
    result = add_standard_features(
        sample_bars(),
        sma_windows=(3,),
        ema_windows=(3,),
        atr_window=3,
        rsi_window=3,
        roc_window=3,
        volatility_window=3,
    )

    expected = {
        "sma_3",
        "ema_3",
        "rolling_high_20",
        "rolling_low_20",
        "return_1",
        "return_5",
        "volatility_3",
        "atr_3",
        "rsi_3",
        "roc_3",
    }

    assert expected.issubset(set(result.columns))
    assert result.height == 20


def test_feature_registry():
    registry = FeatureRegistry()

    registry.register(
        "returns",
        lambda bars: returns(bars, periods=1),
    )

    assert registry.names() == ("returns",)

    result = registry.apply(
        sample_bars(),
        ["returns"],
    )

    assert "return_1" in result.columns


def test_feature_registry_duplicate_rejected():
    registry = FeatureRegistry()

    registry.register(
        "test",
        lambda bars: bars,
    )

    with pytest.raises(ValueError):
        registry.register(
            "test",
            lambda bars: bars,
        )


def test_invalid_window_rejected():
    with pytest.raises(ValueError):
        rolling_mean(sample_bars(), 0)

    with pytest.raises(ValueError):
        atr(sample_bars(), 0)

    with pytest.raises(ValueError):
        rsi(sample_bars(), 0)
