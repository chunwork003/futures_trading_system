from __future__ import annotations

from datetime import date, datetime, time

import polars as pl

from trading_calendar.session import SessionType


DAY_OPEN = time(8, 45)
DAY_CLOSE = time(13, 45)

NIGHT_OPEN = time(15, 0)
NIGHT_CLOSE = time(5, 0)


class SessionNormalizer:
    def __init__(self, trading_calendar):
        self.trading_calendar = trading_calendar

        self._calendar_cache = {}
        self._next_trading_day_cache = {}

        self._load_calendar_cache()

    def _load_calendar_cache(self):
        conn = self.trading_calendar.repository._connect()

        try:
            rows = conn.execute(
                """
                SELECT
                    trade_date,
                    is_trading_day,
                    day_session,
                    night_session
                FROM trading_calendar
                ORDER BY trade_date
                """
            ).fetchall()
        finally:
            conn.close()

        self._calendar_cache = {
            row[0]: {
                "is_trading_day": bool(row[1]),
                "day_session": bool(row[2]),
                "night_session": bool(row[3]),
            }
            for row in rows
        }

        trading_dates = [
            trade_date
            for trade_date, info in self._calendar_cache.items()
            if info["is_trading_day"]
        ]

        all_dates = sorted(self._calendar_cache.keys())

        # 建立每個日期對應的下一個實際交易日
        for current_date in all_dates:
            next_trade_date = next(
                (
                    trade_date
                    for trade_date in trading_dates
                    if trade_date > current_date
                ),
                None,
            )

            self._next_trading_day_cache[current_date] = (
                next_trade_date
            )

    def _get_next_trading_day(
        self,
        current_date: date,
        include_current: bool,
    ):
        info = self._calendar_cache.get(current_date)

        if (
            include_current
            and info is not None
            and info["is_trading_day"]
        ):
            return current_date

        return self._next_trading_day_cache.get(
            current_date
        )

    def normalize_row(
        self,
        timestamp: datetime,
        source_trade_date: date,
    ) -> tuple[str, date]:

        timestamp_date = timestamp.date()
        current_time = timestamp.time()

        # -------------------------
        # DAY
        # -------------------------
        if DAY_OPEN <= current_time < DAY_CLOSE:

            info = self._calendar_cache.get(
                timestamp_date
            )

            if (
                info is not None
                and info["is_trading_day"]
                and info["day_session"]
            ):
                return (
                    SessionType.DAY.value,
                    timestamp_date,
                )

            return (
                "NONE",
                source_trade_date,
            )

        # -------------------------
        # NIGHT after 15:00
        # -------------------------
        if current_time >= NIGHT_OPEN:

            next_trade_date = (
                self._get_next_trading_day(
                    timestamp_date,
                    include_current=False,
                )
            )

            if next_trade_date is not None:

                info = self._calendar_cache.get(
                    next_trade_date
                )

                if (
                    info is not None
                    and info["night_session"]
                ):
                    return (
                        SessionType.NIGHT.value,
                        next_trade_date,
                    )

            return (
                "NONE",
                source_trade_date,
            )

        # -------------------------
        # NIGHT before 05:00
        # -------------------------
        if current_time < NIGHT_CLOSE:

            trade_date = (
                self._get_next_trading_day(
                    timestamp_date,
                    include_current=True,
                )
            )

            if trade_date is not None:

                info = self._calendar_cache.get(
                    trade_date
                )

                if (
                    info is not None
                    and info["night_session"]
                ):
                    return (
                        SessionType.NIGHT.value,
                        trade_date,
                    )

            return (
                "NONE",
                source_trade_date,
            )

        # -------------------------
        # Outside trading session
        # -------------------------
        return (
            "NONE",
            source_trade_date,
        )

    def normalize(
        self,
        df: pl.DataFrame,
    ) -> pl.DataFrame:

        required = {
            "timestamp",
            "trade_date",
        }

        missing = required - set(df.columns)

        if missing:
            raise ValueError(
                f"Missing required columns: {sorted(missing)}"
            )

        sessions = []
        trade_dates = []

        for row in df.iter_rows(named=True):

            session, trade_date = self.normalize_row(
                timestamp=row["timestamp"],
                source_trade_date=row["trade_date"],
            )

            sessions.append(session)
            trade_dates.append(trade_date)

        return df.with_columns(
            [
                pl.Series(
                    "session",
                    sessions,
                    dtype=pl.String,
                ),
                pl.Series(
                    "normalized_trade_date",
                    trade_dates,
                    dtype=pl.Date,
                ),
            ]
        )