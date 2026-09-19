import polars as pl

from features import FeatureBuilder


def test_feature_builder():
    df = pl.DataFrame(
        {
            "open": [100.0, 101.0],
            "high": [102.0, 103.0],
            "low": [99.0, 100.0],
            "close": [101.0, 102.0],
        }
    )

    result = FeatureBuilder().build(df)

    expected_columns = [
        "bar_range",
        "body",
        "body_abs",
        "upper_wick",
        "lower_wick",
        "return_points",
        "return_pct",
        "sma_5",
        "sma_20",
        "sma_60",
        "ema_20",
        "ema_60",
        "close_vs_sma20",
        "close_vs_sma20_pct",
        "sma20_slope",
        "sma20_slope_5",
    ]

    for column in expected_columns:
        assert column in result.columns
