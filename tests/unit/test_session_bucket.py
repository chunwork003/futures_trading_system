from datetime import date, datetime

import polars as pl
import pytest

from aggregation.session_bucket import (
    add_bucket_start,
    calculate_bucket_start,
)


TRADE_DATE = date(2026, 9, 18)


def test_day_5m_bucket():
    result = calculate_bucket_start(
        timestamp=datetime(2026, 9, 18, 8, 45),
        trade_date=TRADE_DATE,
        session="DAY",
        timeframe_minutes=5,
    )

    assert result == datetime(
        2026, 9, 18, 8, 45
    )


def test_day_5m_second_bucket():
    result = calculate_bucket_start(
        timestamp=datetime(2026, 9, 18, 8, 49),
        trade_date=TRADE_DATE,
        session="DAY",
        timeframe_minutes=5,
    )

    assert result == datetime(
        2026, 9, 18, 8, 45
    )


def test_day_5m_next_bucket():
    result = calculate_bucket_start(
        timestamp=datetime(2026, 9, 18, 8, 50),
        trade_date=TRADE_DATE,
        session="DAY",
        timeframe_minutes=5,
    )

    assert result == datetime(
        2026, 9, 18, 8, 50
    )


def test_day_15m_alignment():
    result = calculate_bucket_start(
        timestamp=datetime(2026, 9, 18, 9, 14),
        trade_date=TRADE_DATE,
        session="DAY",
        timeframe_minutes=15,
    )

    assert result == datetime(
        2026, 9, 18, 9, 0
    )


def test_day_15m_boundary():
    result = calculate_bucket_start(
        timestamp=datetime(2026, 9, 18, 9, 15),
        trade_date=TRADE_DATE,
        session="DAY",
        timeframe_minutes=15,
    )

    assert result == datetime(
        2026, 9, 18, 9, 15
    )


def test_night_starts_previous_calendar_day():
    result = calculate_bucket_start(
        timestamp=datetime(2026, 9, 17, 15, 0),
        trade_date=TRADE_DATE,
        session="NIGHT",
        timeframe_minutes=5,
    )

    assert result == datetime(
        2026, 9, 17, 15, 0
    )


def test_night_before_midnight():
    result = calculate_bucket_start(
        timestamp=datetime(2026, 9, 17, 23, 59),
        trade_date=TRADE_DATE,
        session="NIGHT",
        timeframe_minutes=60,
    )

    assert result == datetime(
        2026, 9, 17, 23, 0
    )


def test_night_after_midnight():
    result = calculate_bucket_start(
        timestamp=datetime(2026, 9, 18, 0, 1),
        trade_date=TRADE_DATE,
        session="NIGHT",
        timeframe_minutes=60,
    )

    assert result == datetime(
        2026, 9, 18, 0, 0
    )


def test_night_0459():
    result = calculate_bucket_start(
        timestamp=datetime(2026, 9, 18, 4, 59),
        trade_date=TRADE_DATE,
        session="NIGHT",
        timeframe_minutes=60,
    )

    assert result == datetime(
        2026, 9, 18, 4, 0
    )


def test_dataframe_bucket():
    df = pl.DataFrame(
        {
            "timestamp": [
                datetime(2026, 9, 18, 8, 45),
                datetime(2026, 9, 18, 8, 49),
                datetime(2026, 9, 18, 8, 50),
                datetime(2026, 9, 18, 9, 1),
            ],
            "trade_date": [
                TRADE_DATE,
                TRADE_DATE,
                TRADE_DATE,
                TRADE_DATE,
            ],
            "session": [
                "DAY",
                "DAY",
                "DAY",
                "DAY",
            ],
        }
    )

    result = add_bucket_start(
        df,
        timeframe_minutes=5,
    )

    assert result["bucket_start"].to_list() == [
        datetime(2026, 9, 18, 8, 45),
        datetime(2026, 9, 18, 8, 45),
        datetime(2026, 9, 18, 8, 50),
        datetime(2026, 9, 18, 9, 0),
    ]


def test_invalid_session():
    with pytest.raises(ValueError):
        calculate_bucket_start(
            timestamp=datetime(2026, 9, 18, 10, 0),
            trade_date=TRADE_DATE,
            session="NONE",
            timeframe_minutes=5,
        )


def test_invalid_timeframe():
    with pytest.raises(ValueError):
        calculate_bucket_start(
            timestamp=datetime(2026, 9, 18, 10, 0),
            trade_date=TRADE_DATE,
            session="DAY",
            timeframe_minutes=0,
        )