from datetime import date

from trading_calendar.contract_dates import (
    third_wednesday,
)


def test_september_2026_third_wednesday():

    result = third_wednesday(
        2026,
        9,
    )

    assert result == date(
        2026,
        9,
        16,
    )


def test_december_2026_third_wednesday():

    result = third_wednesday(
        2026,
        12,
    )

    assert result == date(
        2026,
        12,
        16,
    )