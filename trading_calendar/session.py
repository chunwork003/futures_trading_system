from datetime import date, datetime, time
from enum import Enum


class SessionType(str, Enum):
    DAY = "DAY"
    NIGHT = "NIGHT"


class Session:

    def __init__(
        self,
        session_type: SessionType,
        open_time: time,
        close_time: time,
    ):
        self.session_type = session_type
        self.open_time = open_time
        self.close_time = close_time

    @property
    def is_day(self) -> bool:
        return self.session_type == SessionType.DAY

    @property
    def is_night(self) -> bool:
        return self.session_type == SessionType.NIGHT

    @property
    def crosses_midnight(self) -> bool:
        return self.close_time < self.open_time

    def contains(self, timestamp: datetime) -> bool:
        current_time = timestamp.time()

        if not self.crosses_midnight:
            return (
                self.open_time
                <= current_time
                < self.close_time
            )

        return (
            current_time >= self.open_time
            or current_time < self.close_time
        )

    def get_trade_date(
        self,
        timestamp: datetime,
        trade_date: date,
    ) -> date:
        """
        Return the trading date assigned to this session.

        For a night session that crosses midnight,
        timestamps after midnight still belong to
        the previous trading date.
        """

        if not self.crosses_midnight:
            return trade_date

        current_time = timestamp.time()

        if current_time <= self.close_time:
            return trade_date

        return timestamp.date()
