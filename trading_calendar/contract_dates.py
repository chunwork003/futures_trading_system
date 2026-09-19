from datetime import date, timedelta


def third_wednesday(year: int, month: int) -> date:
    """
    計算指定月份的第三個星期三。
    """

    first_day = date(year, month, 1)

    days_until_wednesday = (
        2 - first_day.weekday()
    ) % 7

    first_wednesday = (
        first_day + timedelta(days=days_until_wednesday)
    )

    return first_wednesday + timedelta(days=14)


def calculate_last_trade_date(
    year: int,
    month: int,
    trading_calendar,
) -> date:
    """
    計算 TXF 實際最後交易日。

    規則：
    1. 理論最後交易日 = 交割月份第三個星期三
    2. 若該日不是交易日，順延至下一個交易日
    """

    theoretical_date = third_wednesday(
        year,
        month,
    )

    if trading_calendar.is_trading_day(
        theoretical_date
    ):
        return theoretical_date

    current = theoretical_date + timedelta(days=1)

    while not trading_calendar.is_trading_day(current):
        current += timedelta(days=1)

    return current