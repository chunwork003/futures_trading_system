from datetime import datetime

import polars as pl
import pytest

from features.price import add_price_features


def make_bars() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "timestamp": [
                datetime(2026, 1, 2, 8, 45),
                datetime(2026, 1, 2, 8, 46),
                datetime(2026, 1, 2, 8, 47),
            ],
            "open": [100.0, 102.0, 101.0],
            "high": [105.0, 106.0, 104.0],
            "low": [99.0, 100.0, 100.0],
            "close": [102.0, 101.0, 103.0],
        }
    )


def test_price_features():
    result = add_price_features(make_bars())

    assert result["bar_range"].to_list() == [
        6.0,
        6.0,
        4.0,
    ]

    assert result["body"].to_list() == [
        2.0,
        -1.0,
        2.0,
    ]

    assert result["body_abs"].to_list() == [
        2.0,
        1.0,
        2.0,
    ]

    assert result["upper_wick"].to_list() == [
        3.0,
        4.0,
        1.0,
    ]

    assert result["lower_wick"].to_list() == [
        1.0,
        1.0,
        1.0,
    ]


def test_return_features():
    result = add_price_features(make_bars())

    assert result["return_points"].to_list() == [
        None,
        -1.0,
        2.0,
    ]

    assert result["return_pct"][0] is None
    assert result["return_pct"][1] == pytest.approx(-1 / 102)
    assert result["return_pct"][2] == pytest.approx(2 / 101)
