from datetime import date

from trading_calendar.repository import (
    CalendarRepository,
)


class TradingCalendar:

    def __init__(
        self,
        database_path: str = "database/market.duckdb",
    ):
        self.repository = CalendarRepository(
            database_path
        )

    def get_calendar(
        self,
        trade_date: date,
    ):
        return self.repository.get(
            trade_date
        )

    def is_trading_day(
        self,
        trade_date: date,
    ) -> bool:

        return self.repository.is_trading_day(
            trade_date
        )

    def has_day_session(
        self,
        trade_date: date,
    ) -> bool:

        return self.repository.has_day_session(
            trade_date
        )

    def has_night_session(
        self,
        trade_date: date,
    ) -> bool:

        return self.repository.has_night_session(
            trade_date
        )

    def get_next_trading_day(
        self,
        trade_date: date,
        include_current: bool = False,
    ):
        result = self.repository.get_next_trading_day(
            trade_date,
            include_current=include_current,
        )

        if result is None:
            return None

        return result[0]
    def get_previous_trading_day(
        self,
        trade_date: date,
        include_current: bool = False,
    ):
        result = self.repository.get_previous_trading_day(
            trade_date,
            include_current=include_current,
        )

        if result is None:
            return None

        return result[0]