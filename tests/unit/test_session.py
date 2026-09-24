from datetime import datetime, time

from trading_calendar.session import Session, SessionType


def test_day_session():

    session = Session(
        SessionType.DAY,
        time(8, 45),
        time(13, 45),
    )

    assert session.contains(
        datetime(2026, 9, 15, 9, 0)
    )

    assert not session.contains(
        datetime(2026, 9, 15, 13, 45)
    )

    assert not session.contains(
        datetime(2026, 9, 15, 14, 0)
    )


def test_day_session_uses_open_inclusive_close_exclusive_interval():
    session = Session(
        SessionType.DAY,
        time(8, 45),
        time(13, 45),
    )

    assert session.contains(datetime(2026, 9, 15, 8, 45))
    assert session.contains(datetime(2026, 9, 15, 13, 44, 59, 999999))
    assert not session.contains(datetime(2026, 9, 15, 13, 45))


def test_night_session_before_midnight():

    session = Session(
        SessionType.NIGHT,
        time(15, 0),
        time(5, 0),
    )

    assert session.contains(
        datetime(2026, 9, 15, 20, 0)
    )


def test_night_session_after_midnight():

    session = Session(
        SessionType.NIGHT,
        time(15, 0),
        time(5, 0),
    )

    assert session.contains(
        datetime(2026, 9, 16, 1, 0)
    )


def test_cross_midnight_session_uses_open_inclusive_close_exclusive_interval():
    session = Session(
        SessionType.NIGHT,
        time(15, 0),
        time(5, 0),
    )

    assert session.contains(datetime(2026, 9, 15, 15, 0))
    assert session.contains(datetime(2026, 9, 15, 23, 59))
    assert session.contains(datetime(2026, 9, 16, 0, 0))
    assert session.contains(datetime(2026, 9, 16, 4, 59, 59, 999999))
    assert not session.contains(datetime(2026, 9, 16, 5, 0))


def test_night_session_outside():

    session = Session(
        SessionType.NIGHT,
        time(15, 0),
        time(5, 0),
    )

    assert not session.contains(
        datetime(2026, 9, 15, 12, 0)
    )


def test_crosses_midnight():

    session = Session(
        SessionType.NIGHT,
        time(15, 0),
        time(5, 0),
    )

    assert session.crosses_midnight is True
