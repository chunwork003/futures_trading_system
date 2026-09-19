from datetime import datetime

from trading_calendar.session import SessionType
from trading_calendar.session_resolver import SessionResolver
from trading_calendar.trading_calendar import TradingCalendar


def create_resolver():

    calendar = TradingCalendar(
        "database/market.duckdb"
    )

    return SessionResolver(calendar)


def test_day_session_resolution():

    resolver = create_resolver()

    result = resolver.resolve(
        datetime(2026, 9, 15, 9, 30)
    )

    assert result.session_type == SessionType.DAY
    assert str(result.trade_date) == "2026-09-15"
    assert result.is_trading is True


def test_day_session_boundary_open():

    resolver = create_resolver()

    result = resolver.resolve(
        datetime(2026, 9, 15, 8, 45)
    )

    assert result.session_type == SessionType.DAY


def test_day_session_boundary_close():

    resolver = create_resolver()

    result = resolver.resolve(
        datetime(2026, 9, 15, 13, 45)
    )

    assert result.session_type is None
    assert result.is_trading is False


def test_night_session_before_midnight():

    resolver = create_resolver()

    result = resolver.resolve(
        datetime(2026, 9, 15, 20, 0)
    )

    assert result.session_type == SessionType.NIGHT

    # Night session belongs to next trading date.
    assert str(result.trade_date) == "2026-09-16"


def test_night_session_after_midnight():

    resolver = create_resolver()

    result = resolver.resolve(
        datetime(2026, 9, 16, 1, 30)
    )

    assert result.session_type == SessionType.NIGHT

    assert str(result.trade_date) == "2026-09-16"


def test_night_session_boundary_0500():

    resolver = create_resolver()

    result = resolver.resolve(
        datetime(2026, 9, 16, 5, 0)
    )

    assert result.session_type is None


def test_outside_session():

    resolver = create_resolver()

    result = resolver.resolve(
        datetime(2026, 9, 15, 14, 30)
    )

    assert result.session_type is None
    assert result.is_trading is False


def test_friday_night_belongs_to_monday():

    resolver = create_resolver()

    result = resolver.resolve(
        datetime(2026, 9, 18, 20, 0)
    )

    assert result.session_type == SessionType.NIGHT

    # 2026-09-18 is Friday.
    # The next trading date is Monday 2026-09-21.
    assert str(result.trade_date) == "2026-09-21"


def test_saturday_early_morning_belongs_to_monday():

    resolver = create_resolver()

    result = resolver.resolve(
        datetime(2026, 9, 19, 3, 0)
    )

    assert result.session_type == SessionType.NIGHT

    assert str(result.trade_date) == "2026-09-21"