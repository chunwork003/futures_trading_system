from datetime import date, datetime, timedelta

import polars as pl

from aggregation.bar_aggregator import (
    aggregate_bars,
)


def make_day_data() -> pl.DataFrame:
    start = datetime(
        2026, 9, 18, 8, 45
    )

    rows = []

    for i in range(60):
        timestamp = start + timedelta(
            minutes=i
        )

        price = 1000 + i

        rows.append(
            {
                "timestamp": timestamp,
                "trade_date": date(
                    2026, 9, 18
                ),
                "symbol": "TX",
                "contract": "TX202609",
                "timeframe": "1m",
                "open": float(price),
                "high": float(price + 2),
                "low": float(price - 1),
                "close": float(price + 1),
                "volume": 10,
                "session": "DAY",
                "source": "test",
            }
        )

    return pl.DataFrame(rows)


def test_5m_aggregation():
    df = make_day_data()

    result = aggregate_bars(
        df,
        "5m",
    )

    assert result.height == 12

    assert result["timestamp"][0] == datetime(
        2026, 9, 18, 8, 45
    )

    assert result["timestamp"][-1] == datetime(
        2026, 9, 18, 9, 40
    )

    assert result["open"][0] == 1000

    assert result["close"][0] == 1005

    assert result["high"][0] == 1006

    assert result["low"][0] == 999

    assert result["volume"][0] == 50

    assert result["trade_count"][0] == 5


def test_15m_aggregation():
    df = make_day_data()

    result = aggregate_bars(
        df,
        "15m",
    )

    assert result.height == 4

    assert result["timestamp"][0] == datetime(
        2026, 9, 18, 8, 45
    )

    assert result["timestamp"][1] == datetime(
        2026, 9, 18, 9, 0
    )

    assert result["trade_count"].to_list() == [
        15,
        15,
        15,
        15,
    ]


def test_30m_aggregation():
    df = make_day_data()

    result = aggregate_bars(
        df,
        "30m",
    )

    assert result.height == 2

    assert result["trade_count"].to_list() == [
        30,
        30,
    ]


def test_60m_aggregation():
    df = make_day_data()

    result = aggregate_bars(
        df,
        "60m",
    )

    assert result.height == 1

    assert result["timestamp"][0] == datetime(
        2026, 9, 18, 8, 45
    )

    assert result["trade_count"][0] == 60

def make_day_and_night_data() -> pl.DataFrame:
    rows = []

    # NIGHT:
    # 2026-09-17 15:00 -> 2026-09-18 04:59
    night_start = datetime(
        2026, 9, 17, 15, 0
    )

    for i in range(14 * 60):
        timestamp = night_start + timedelta(
            minutes=i
        )

        price = 2000 + i

        rows.append(
            {
                "timestamp": timestamp,
                "trade_date": date(
                    2026, 9, 18
                ),
                "symbol": "TX",
                "contract": "TX202609",
                "timeframe": "1m",
                "open": float(price),
                "high": float(price + 2),
                "low": float(price - 1),
                "close": float(price + 1),
                "volume": 10,
                "session": "NIGHT",
                "source": "test",
            }
        )

    # DAY:
    # 2026-09-18 08:45 -> 13:44
    day_start = datetime(
        2026, 9, 18, 8, 45
    )

    for i in range(5 * 60):
        timestamp = day_start + timedelta(
            minutes=i
        )

        price = 3000 + i

        rows.append(
            {
                "timestamp": timestamp,
                "trade_date": date(
                    2026, 9, 18
                ),
                "symbol": "TX",
                "contract": "TX202609",
                "timeframe": "1m",
                "open": float(price),
                "high": float(price + 2),
                "low": float(price - 1),
                "close": float(price + 1),
                "volume": 10,
                "session": "DAY",
                "source": "test",
            }
        )

    return pl.DataFrame(rows)


def test_night_cross_midnight_5m():
    df = make_day_and_night_data()

    result = aggregate_bars(
        df,
        "5m",
    )

    night = result.filter(
        pl.col("session") == "NIGHT"
    )

    assert night.height == 168

    assert night["trade_date"].unique().to_list() == [
        date(2026, 9, 18)
    ]

    assert night["timestamp"][0] == datetime(
        2026, 9, 17, 15, 0
    )

    assert night["timestamp"][-1] == datetime(
        2026, 9, 18, 4, 55
    )


def test_day_and_night_are_separate():
    df = make_day_and_night_data()

    result = aggregate_bars(
        df,
        "5m",
    )

    day = result.filter(
        pl.col("session") == "DAY"
    )

    night = result.filter(
        pl.col("session") == "NIGHT"
    )

    assert day.height == 60

    assert night.height == 168

    assert day["trade_date"].unique().to_list() == [
        date(2026, 9, 18)
    ]

    assert night["trade_date"].unique().to_list() == [
        date(2026, 9, 18)
    ]


def test_night_midnight_does_not_reset_bucket():
    df = pl.DataFrame(
        {
            "timestamp": [
                datetime(2026, 9, 17, 23, 59),
                datetime(2026, 9, 18, 0, 0),
                datetime(2026, 9, 18, 0, 1),
                datetime(2026, 9, 18, 0, 4),
            ],
            "trade_date": [
                date(2026, 9, 18),
                date(2026, 9, 18),
                date(2026, 9, 18),
                date(2026, 9, 18),
            ],
            "symbol": [
                "TX",
                "TX",
                "TX",
                "TX",
            ],
            "contract": [
                "TX202609",
                "TX202609",
                "TX202609",
                "TX202609",
            ],
            "timeframe": [
                "1m",
                "1m",
                "1m",
                "1m",
            ],
            "open": [
                1000.0,
                1001.0,
                1002.0,
                1003.0,
            ],
            "high": [
                1002.0,
                1003.0,
                1004.0,
                1005.0,
            ],
            "low": [
                999.0,
                1000.0,
                1001.0,
                1002.0,
            ],
            "close": [
                1001.0,
                1002.0,
                1003.0,
                1004.0,
            ],
            "volume": [
                10,
                10,
                10,
                10,
            ],
            "session": [
                "NIGHT",
                "NIGHT",
                "NIGHT",
                "NIGHT",
            ],
            "source": [
                "test",
                "test",
                "test",
                "test",
            ],
        }
    )

    result = aggregate_bars(
        df,
        "5m",
    )

    assert result.height == 2

    assert result["timestamp"].to_list() == [
        datetime(2026, 9, 17, 23, 55),
        datetime(2026, 9, 18, 0, 0),
    ]

    assert result["trade_date"].unique().to_list() == [
        date(2026, 9, 18)
    ]