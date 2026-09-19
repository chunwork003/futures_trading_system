from datetime import date, time

import polars as pl


def create_calendar_fixture() -> pl.DataFrame:

    return pl.DataFrame(
        {
            "trade_date": [
                date(2026, 9, 15),
                date(2026, 9, 16),
                date(2026, 9, 17),
            ],

            "is_trading_day": [
                True,
                True,
                True,
            ],

            "day_session": [
                True,
                True,
                True,
            ],

            "night_session": [
                True,
                True,
                True,
            ],

            "day_open": [
                time(8, 45),
                time(8, 45),
                time(8, 45),
            ],

            "day_close": [
                time(13, 45),
                time(13, 45),
                time(13, 45),
            ],

            "night_open": [
                time(15, 0),
                time(15, 0),
                time(15, 0),
            ],

            "night_close": [
                time(5, 0),
                time(5, 0),
                time(5, 0),
            ],

            "notes": [
                None,
                None,
                None,
            ],
        }
    )