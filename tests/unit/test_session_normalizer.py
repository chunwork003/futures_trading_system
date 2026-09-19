from datetime import date, datetime

import polars as pl

from trading_calendar.trading_calendar import TradingCalendar
from trading_calendar.session_normalizer import SessionNormalizer


def create_normalizer():

    calendar = TradingCalendar(
        "database/market.duckdb"
    )

    return SessionNormalizer(calendar)


def test_day_session():

    normalizer = create_normalizer()

    session, trade_date = normalizer.normalize_row(
        datetime(2026, 9, 15, 9, 30),
        date(2026, 9, 15),
    )

    assert session == "DAY"
    assert trade_date == date(2026, 9, 15)


def test_day_session_boundary():

    normalizer = create_normalizer()

    session, trade_date = normalizer.normalize_row(
        datetime(2026, 9, 15, 8, 45),
        date(2026, 9, 15),
    )

    assert session == "DAY"
    assert trade_date == date(2026, 9, 15)


def test_day_session_close():

    normalizer = create_normalizer()

    session, _ = normalizer.normalize_row(
        datetime(2026, 9, 15, 13, 45),
        date(2026, 9, 15),
    )

    assert session == "NONE"


def test_night_before_midnight():

    normalizer = create_normalizer()

    session, trade_date = normalizer.normalize_row(
        datetime(2026, 9, 15, 20, 0),
        date(2026, 9, 16),
    )

    assert session == "NIGHT"
    assert trade_date == date(2026, 9, 16)


def test_night_after_midnight():

    normalizer = create_normalizer()

    session, trade_date = normalizer.normalize_row(
        datetime(2026, 9, 16, 1, 30),
        date(2026, 9, 16),
    )

    assert session == "NIGHT"
    assert trade_date == date(2026, 9, 16)


def test_friday_night_to_monday():

    normalizer = create_normalizer()

    session, trade_date = normalizer.normalize_row(
        datetime(2026, 9, 18, 20, 0),
        date(2026, 9, 21),
    )

    assert session == "NIGHT"
    assert trade_date == date(2026, 9, 21)


def test_saturday_early_morning_to_monday():

    normalizer = create_normalizer()

    session, trade_date = normalizer.normalize_row(
        datetime(2026, 9, 19, 3, 0),
        date(2026, 9, 21),
    )

    assert session == "NIGHT"
    assert trade_date == date(2026, 9, 21)


def test_0500_is_none():

    normalizer = create_normalizer()

    session, _ = normalizer.normalize_row(
        datetime(2026, 9, 16, 5, 0),
        date(2026, 9, 16),
    )

    assert session == "NONE"


def test_dataframe_normalization():

    normalizer = create_normalizer()

    df = pl.DataFrame(
        {
            "timestamp": [
                datetime(2026, 9, 15, 9, 30),
                datetime(2026, 9, 15, 20, 0),
                datetime(2026, 9, 16, 1, 30),
            ],
            "trade_date": [
                date(2026, 9, 15),
                date(2026, 9, 16),
                date(2026, 9, 16),
            ],
        }
    )

    result = normalizer.normalize(df)

    assert result["session"].to_list() == [
        "DAY",
        "NIGHT",
        "NIGHT",
    ]

    assert result["normalized_trade_date"].to_list() == [
        date(2026, 9, 15),
        date(2026, 9, 16),
        date(2026, 9, 16),
    ]