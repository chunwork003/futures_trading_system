from datetime import date, time

from trading_calendar.sources.taifex_rules import (
    get_session_rule,
)


def test_before_night_session():

    rule = get_session_rule(
        date(2017, 5, 14)
    )

    assert rule.night_enabled is False
    assert rule.day_open == time(8, 45)
    assert rule.day_close == time(13, 45)


def test_night_session_start():

    rule = get_session_rule(
        date(2017, 5, 15)
    )

    assert rule.night_enabled is True
    assert rule.night_open == time(15, 0)
    assert rule.night_close == time(5, 0)


def test_current_rule():

    rule = get_session_rule(
        date(2026, 9, 15)
    )

    assert rule.night_enabled is True
    assert rule.day_open == time(8, 45)
    assert rule.day_close == time(13, 45)