from datetime import date
from pathlib import Path

import duckdb


class CalendarRepository:

    def __init__(
        self,
        database_path: str = "database/market.duckdb",
    ):
        self.database_path = Path(database_path)

    def _connect(self):
        return duckdb.connect(
            str(self.database_path)
        )

    def get(
        self,
        trade_date: date,
    ):
        conn = self._connect()

        try:
            return conn.execute(
                """
                SELECT
                    trade_date,
                    is_trading_day,
                    day_session,
                    night_session,
                    day_open,
                    day_close,
                    night_open,
                    night_close,
                    notes
                FROM trading_calendar
                WHERE trade_date = ?
                """,
                [trade_date],
            ).fetchone()

        finally:
            conn.close()

    def exists(
        self,
        trade_date: date,
    ) -> bool:

        conn = self._connect()

        try:
            result = conn.execute(
                """
                SELECT 1
                FROM trading_calendar
                WHERE trade_date = ?
                LIMIT 1
                """,
                [trade_date],
            ).fetchone()

            return result is not None

        finally:
            conn.close()

    def is_trading_day(
        self,
        trade_date: date,
    ) -> bool:

        result = self.get(trade_date)

        if result is None:
            return False

        return bool(result[1])

    def has_day_session(
        self,
        trade_date: date,
    ) -> bool:

        result = self.get(trade_date)

        if result is None:
            return False

        return bool(result[2])

    def has_night_session(
        self,
        trade_date: date,
    ) -> bool:

        result = self.get(trade_date)

        if result is None:
            return False

        return bool(result[3])

    def get_next_trading_day(
        self,
        trade_date: date,
        include_current: bool = False,
    ):
        conn = self._connect()

        try:
            operator = ">=" if include_current else ">"

            return conn.execute(
                f"""
                SELECT trade_date
                FROM trading_calendar
                WHERE trade_date {operator} ?
                  AND is_trading_day = TRUE
                ORDER BY trade_date
                LIMIT 1
                """,
                [trade_date],
            ).fetchone()

        finally:
            conn.close()

    def get_previous_trading_day(
        self,
        trade_date: date,
        include_current: bool = False,
    ):
        conn = self._connect()

        try:
            operator = "<=" if include_current else "<"

            return conn.execute(
                f"""
                SELECT trade_date
                FROM trading_calendar
                WHERE trade_date {operator} ?
                  AND is_trading_day = TRUE
                ORDER BY trade_date DESC
                LIMIT 1
                """,
                [trade_date],
            ).fetchone()

        finally:
            conn.close()