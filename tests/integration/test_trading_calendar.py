from datetime import date

import duckdb

from tests.fixtures.calendar_fixture import (
    create_calendar_fixture,
)

from trading_calendar.loader import (
    TradingCalendarLoader,
)

from trading_calendar.trading_calendar import (
    TradingCalendar,
)


def initialize_test_database(
    database_path,
):

    conn = duckdb.connect(
        str(database_path)
    )

    try:

        conn.execute(
            """
            CREATE TABLE trading_calendar (
                trade_date DATE PRIMARY KEY,
                is_trading_day BOOLEAN NOT NULL,
                day_session BOOLEAN NOT NULL,
                night_session BOOLEAN NOT NULL,
                day_open TIME,
                day_close TIME,
                night_open TIME,
                night_close TIME,
                notes VARCHAR,
                created_at TIMESTAMP
            )
            """
        )

    finally:
        conn.close()


def test_calendar_loader_and_repository(
    tmp_path,
):

    database_path = (
        tmp_path
        / "test_market.duckdb"
    )

    initialize_test_database(
        database_path
    )

    df = create_calendar_fixture()

    loader = TradingCalendarLoader(
        str(database_path)
    )

    loader.load_dataframe(df)

    calendar = TradingCalendar(
        str(database_path)
    )

    assert calendar.is_trading_day(
        date(2026, 9, 15)
    )

    assert calendar.has_day_session(
        date(2026, 9, 15)
    )

    assert calendar.has_night_session(
        date(2026, 9, 15)
    )