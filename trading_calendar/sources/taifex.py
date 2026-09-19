from datetime import date, time, timedelta

import polars as pl


class TAIFEXCalendarSource:
    """
    Generate TAIFEX trading calendar data.

    This source keeps the annual calendar rules and known
    official market-closure exceptions separate from the
    database layer.

    IMPORTANT:
    - This is for calendar generation.
    - Contract-specific expiry session rules are NOT handled here.
    """

    DAY_OPEN = time(8, 45)
    DAY_CLOSE = time(13, 45)

    NIGHT_OPEN = time(15, 0)
    NIGHT_CLOSE = time(5, 0)

    def __init__(self, year: int):
        self.year = year

    def official_closed_dates(self) -> set[date]:
        """
        Official TAIFEX market closure dates for 2026.

        These dates are based on TAIFEX's published 2026
        holiday calendar and subsequent official closure notices.
        """

        if self.year != 2026:
            raise ValueError(
                "Only 2026 calendar is currently supported."
            )

        return {
            # New Year's Day
            date(2026, 1, 1),

            # Chinese New Year
            date(2026, 2, 16),
            date(2026, 2, 17),
            date(2026, 2, 18),
            date(2026, 2, 19),
            date(2026, 2, 20),

            # Peace Memorial Day - substitute holiday
            date(2026, 2, 27),

            # Children's Day / Tomb Sweeping Day
            date(2026, 4, 3),
            date(2026, 4, 6),

            # Labor Day
            date(2026, 5, 1),

            # Dragon Boat Festival
            date(2026, 6, 19),

            # Typhoon closure
            date(2026, 7, 10),

            # Mid-Autumn Festival
            date(2026, 9, 25),

            # Teacher's Day
            date(2026, 9, 28),

            # National Day substitute holiday
            date(2026, 10, 9),

            # Taiwan Retrocession Day
            date(2026, 10, 26),

            # Constitution Day
            date(2026, 12, 25),
        }

    def _date_range(self):
        current = date(self.year, 1, 1)
        end = date(self.year, 12, 31)

        while current <= end:
            yield current
            current += timedelta(days=1)

    def build(self) -> pl.DataFrame:
        closed_dates = self.official_closed_dates()

        rows = []

        for trade_date in self._date_range():

            weekday = trade_date.weekday()

            is_weekday = weekday < 5
            is_closed = trade_date in closed_dates

            is_trading_day = (
                is_weekday
                and not is_closed
            )

            rows.append(
                {
                    "trade_date": trade_date,
                    "is_trading_day": is_trading_day,

                    "day_session": is_trading_day,
                    "night_session": is_trading_day,

                    "day_open": (
                        self.DAY_OPEN
                        if is_trading_day
                        else None
                    ),

                    "day_close": (
                        self.DAY_CLOSE
                        if is_trading_day
                        else None
                    ),

                    "night_open": (
                        self.NIGHT_OPEN
                        if is_trading_day
                        else None
                    ),

                    "night_close": (
                        self.NIGHT_CLOSE
                        if is_trading_day
                        else None
                    ),

                    "notes": (
                        "TAIFEX official market closure"
                        if is_closed
                        else None
                    ),
                }
            )

        return pl.DataFrame(rows)