from datetime import datetime

import polars as pl

from analysis.source_comparison import (
    SourceComparator,
)


def make_df(source: str):

    return pl.DataFrame({
        "timestamp": [
            datetime(2026, 1, 2, 9, 0),
            datetime(2026, 1, 2, 9, 1),
            datetime(2026, 1, 2, 9, 2),
        ],
        "symbol": ["TXF"] * 3,
        "contract": ["TXFR1"] * 3,
        "timeframe": ["1m"] * 3,
        "open": [100.0, 101.0, 102.0],
        "high": [101.0, 102.0, 103.0],
        "low": [99.0, 100.0, 101.0],
        "close": [100.5, 101.5, 102.5],
        "volume": [10, 20, 30],
        "source": [source] * 3,
    })


def test_identical_sources():

    df_a = make_df("a")
    df_b = make_df("b")

    report = SourceComparator().compare(
        df_a,
        df_b,
        source_a="a",
        source_b="b",
    )

    assert report.rows_a == 3
    assert report.rows_b == 3
    assert report.matched_rows == 3
    assert report.missing_in_a == 0
    assert report.missing_in_b == 0
    assert report.price_mismatch_rows == 0
    assert report.volume_mismatch_rows == 0


def test_detect_price_difference():

    df_a = make_df("a")
    df_b = make_df("b").with_columns(
        pl.when(
            pl.col("timestamp")
            == datetime(2026, 1, 2, 9, 1)
        )
        .then(999.0)
        .otherwise(pl.col("close"))
        .alias("close")
    )

    report = SourceComparator().compare(
        df_a,
        df_b,
        source_a="a",
        source_b="b",
    )

    assert report.matched_rows == 3
    assert report.price_mismatch_rows == 1
    assert report.volume_mismatch_rows == 0
    assert report.max_close_diff == 897.5


def test_detect_missing_rows():

    df_a = make_df("a")
    df_b = make_df("b").filter(
        pl.col("timestamp")
        != datetime(2026, 1, 2, 9, 1)
    )

    report = SourceComparator().compare(
        df_a,
        df_b,
        source_a="a",
        source_b="b",
    )

    assert report.rows_a == 3
    assert report.rows_b == 2
    assert report.matched_rows == 2
    assert report.missing_in_a == 0
    assert report.missing_in_b == 1
