from __future__ import annotations

from datetime import date, datetime, time
from typing import Optional

from trading_calendar.session import SessionType


DAY_OPEN = time(8, 45)
DAY_CLOSE = time(13, 45)

NIGHT_OPEN = time(15, 0)
NIGHT_CLOSE = time(5, 0)


class SessionResolution:
    def __init__(
        self,
        session_type: Optional[SessionType],
        trade_date: date,
        session_open: Optional[time] = None,
        session_close: Optional[time] = None,
    ):
        self.session_type = session_type
        self.trade_date = trade_date
        self.session_open = session_open
        self.session_close = session_close

    @property
    def is_trading(self) -> bool:
        return self.session_type is not None


class SessionResolver:
    def __init__(self, trading_calendar):
        self.trading_calendar = trading_calendar

    def _next_trading_day(
        self,
        current_date: date,
        include_current: bool,
    ):
        return self.trading_calendar.get_next_trading_day(
            current_date,
            include_current=include_current,
        )

    def _resolve_night_trade_date(
        self,
        timestamp_date: date,
        current_time: time,
    ):
        # 15:00～23:59：
        # 夜盤屬於下一個實際交易日
        if current_time >= NIGHT_OPEN:
            return self._next_trading_day(
                timestamp_date,
                include_current=False,
            )

        # 00:00～04:59：
        # 屬於當天的交易日夜盤
        #
        # 如果 timestamp_date 是週末/休市日，
        # 必須往後找下一個實際交易日。
        if current_time < NIGHT_CLOSE:
            return self._next_trading_day(
                timestamp_date,
                include_current=True,
            )

        return None

    def resolve(
        self,
        timestamp: datetime,
        contract=None,
    ) -> SessionResolution:

        timestamp_date = timestamp.date()
        current_time = timestamp.time()

        # ---------------------------------------------------------
        # DAY SESSION
        # ---------------------------------------------------------

        if DAY_OPEN <= current_time < DAY_CLOSE:

            calendar = self.trading_calendar.get_calendar(
                timestamp_date
            )

            if (
                calendar is not None
                and bool(calendar[1])
                and bool(calendar[2])
            ):
                if (
                    contract is not None
                    and contract.last_trade_date is not None
                    and timestamp_date == contract.last_trade_date
                ):
                    last_trade_close = time(13, 30)

                    if current_time < last_trade_close:
                        return SessionResolution(
                            session_type=SessionType.DAY,
                            trade_date=timestamp_date,
                            session_open=DAY_OPEN,
                            session_close=last_trade_close,
                        )

                    return SessionResolution(
                        session_type=None,
                        trade_date=timestamp_date,
                    )

                return SessionResolution(
                    session_type=SessionType.DAY,
                    trade_date=timestamp_date,
                    session_open=DAY_OPEN,
                    session_close=DAY_CLOSE,
                )

        # ---------------------------------------------------------
        # NIGHT SESSION
        # ---------------------------------------------------------

        if (
            current_time >= NIGHT_OPEN
            or current_time < NIGHT_CLOSE
        ):
            night_trade_date = self._resolve_night_trade_date(
                timestamp_date=timestamp_date,
                current_time=current_time,
            )

            if night_trade_date is not None:

                calendar = self.trading_calendar.get_calendar(
                    night_trade_date
                )

                if (
                    calendar is not None
                    and bool(calendar[1])
                ):
                    if (
                        contract is not None
                        and contract.last_trade_date is not None
                        and night_trade_date
                        == contract.last_trade_date
                    ):
                        return SessionResolution(
                            session_type=None,
                            trade_date=night_trade_date,
                        )

                    return SessionResolution(
                        session_type=SessionType.NIGHT,
                        trade_date=night_trade_date,
                        session_open=NIGHT_OPEN,
                        session_close=NIGHT_CLOSE,
                    )

        # ---------------------------------------------------------
        # OUTSIDE SESSION
        # ---------------------------------------------------------

        return SessionResolution(
            session_type=None,
            trade_date=timestamp_date,
        )