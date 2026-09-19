from __future__ import annotations

from pathlib import Path

import polars as pl

from aggregation.bar_aggregator import (
    aggregate_bars,
    load_1m_symbol,
)


BASE_PATH = "data/parquet/bar/1m"

SYMBOLS = [
    "TX",
    "MTX",
    "TMF",
]

TIMEFRAMES = [
    "5m",
    "15m",
    "30m",
    "60m",
]


def validate_session(df: pl.DataFrame) -> None:
    print("\n[1] SESSION VALIDATION")

    invalid_session = df.filter(
        ~pl.col("session").is_in(
            ["DAY", "NIGHT"]
        )
    )

    if invalid_session.height > 0:
        raise AssertionError(
            f"Invalid session rows: "
            f"{invalid_session.height:,}"
        )

    print("OK - all rows are DAY/NIGHT")

def validate_day_boundaries(
    df: pl.DataFrame,
) -> None:
    print("\n[2] DAY SESSION TIME DISTRIBUTION")

    day = (
        df
        .filter(pl.col("session") == "DAY")
        .with_columns(
            pl.col("timestamp")
            .dt.time()
            .alias("time")
        )
    )

    print(
        f"DAY rows: {day.height:,}"
    )

    print("\nEarliest DAY timestamps:")

    print(
        day
        .select("timestamp")
        .sort("timestamp")
        .head(10)
    )

    print("\nLatest DAY timestamps:")

    print(
        day
        .select("timestamp")
        .sort("timestamp", descending=True)
        .head(10)
    )

    print("\nDAY time range:")

    print(
        day
        .select(
            [
                pl.col("timestamp")
                .min()
                .alias("min_timestamp"),

                pl.col("timestamp")
                .max()
                .alias("max_timestamp"),
            ]
        )
    )

    print("\nDAY rows by hour:")

    hour_counts = (
        day
        .with_columns(
            pl.col("timestamp")
            .dt.hour()
            .alias("hour")
        )
        .group_by("hour")
        .len()
        .sort("hour")
    )

    print(hour_counts)

    print("\nDAY rows outside expected 08:45-13:45:")

    outside = day.filter(
        (pl.col("timestamp").dt.time() < pl.time(8, 45))
        | (
            pl.col("timestamp").dt.time()
            >= pl.time(13, 45)
        )
    )

    print(
        f"outside rows: {outside.height:,}"
    )

    if outside.height > 0:
        print("\nFirst outside examples:")

        print(
            outside
            .select(
                [
                    "timestamp",
                    "trade_date",
                    "symbol",
                    "contract",
                    "session",
                ]
            )
            .sort("timestamp")
            .head(20)
        )


def validate_night_boundaries(
    df: pl.DataFrame,
) -> None:
    print("\n[3] NIGHT SESSION BOUNDARY")

    night = df.filter(
        pl.col("session") == "NIGHT"
    )

    invalid = night.filter(
        ~(
            (
                pl.col("timestamp").dt.time()
                >= pl.time(15, 0)
            )
            |
            (
                pl.col("timestamp").dt.time()
                < pl.time(5, 0)
            )
        )
    )

    if invalid.height > 0:
        raise AssertionError(
            f"Invalid NIGHT rows: "
            f"{invalid.height:,}"
        )

    print(
        f"OK - NIGHT rows: "
        f"{night.height:,}"
    )


def validate_ohlcv(
    df: pl.DataFrame,
) -> None:
    print("\n[4] OHLCV VALIDATION")

    invalid = df.filter(
        (pl.col("high") < pl.col("open"))
        | (pl.col("high") < pl.col("close"))
        | (pl.col("low") > pl.col("open"))
        | (pl.col("low") > pl.col("close"))
        | (pl.col("volume") < 0)
    )

    if invalid.height > 0:
        raise AssertionError(
            f"Invalid OHLCV rows: "
            f"{invalid.height:,}"
        )

    print("OK - OHLCV valid")

def validate_night_boundaries(
    df: pl.DataFrame,
) -> None:
    print("\n[3] NIGHT SESSION TIME DISTRIBUTION")

    night = (
        df
        .filter(pl.col("session") == "NIGHT")
        .with_columns(
            pl.col("timestamp")
            .dt.time()
            .alias("time")
        )
    )

    print(
        f"NIGHT rows: {night.height:,}"
    )

    print("\nEarliest NIGHT timestamps:")

    print(
        night
        .select(
            [
                "timestamp",
                "trade_date",
                "symbol",
                "contract",
                "session",
            ]
        )
        .sort("timestamp")
        .head(10)
    )

    print("\nLatest NIGHT timestamps:")

    print(
        night
        .select(
            [
                "timestamp",
                "trade_date",
                "symbol",
                "contract",
                "session",
            ]
        )
        .sort("timestamp", descending=True)
        .head(10)
    )

    print("\nNIGHT rows by hour:")

    hour_counts = (
        night
        .with_columns(
            pl.col("timestamp")
            .dt.hour()
            .alias("hour")
        )
        .group_by("hour")
        .len()
        .sort("hour")
    )

    print(hour_counts)

    outside = night.filter(
        ~(
            (
                pl.col("timestamp").dt.time()
                >= pl.time(15, 0)
            )
            |
            (
                pl.col("timestamp").dt.time()
                < pl.time(5, 0)
            )
        )
    )

    print(
        "\nNIGHT rows outside expected "
        "15:00-04:59:"
    )

    print(
        f"outside rows: {outside.height:,}"
    )

    if outside.height > 0:
        print("\nOutside NIGHT examples:")

        print(
            outside
            .select(
                [
                    "timestamp",
                    "trade_date",
                    "symbol",
                    "contract",
                    "session",
                ]
            )
            .sort("timestamp")
            .head(50)
        )
def validate_bucket(
    result: pl.DataFrame,
    timeframe: str,
) -> None:
    print(
        f"\n[6] BUCKET VALIDATION - {timeframe}"
    )

    if result.is_empty():
        print("WARNING - no rows")
        return

    duplicated = (
        result
        .group_by(
            [
                "trade_date",
                "symbol",
                "contract",
                "session",
                "timestamp",
            ]
        )
        .len()
        .filter(pl.col("len") > 1)
    )

    if duplicated.height > 0:
        raise AssertionError(
            f"Duplicate buckets: "
            f"{duplicated.height:,}"
        )

    # DAY bucket must remain inside DAY session.
    day_invalid = result.filter(
        (pl.col("session") == "DAY")
        & (
            (pl.col("timestamp").dt.time() < pl.time(8, 45))
            | (
                pl.col("timestamp").dt.time()
                >= pl.time(13, 45)
            )
        )
    )

    if day_invalid.height > 0:
        raise AssertionError(
            f"Invalid DAY buckets: "
            f"{day_invalid.height:,}"
        )

    # NIGHT bucket must remain in:
    # 15:00 ~ 23:59 or 00:00 ~ 04:59
    night_invalid = result.filter(
        (pl.col("session") == "NIGHT")
        & ~(
            (
                pl.col("timestamp").dt.time()
                >= pl.time(15, 0)
            )
            |
            (
                pl.col("timestamp").dt.time()
                < pl.time(5, 0)
            )
        )
    )

    if night_invalid.height > 0:
        raise AssertionError(
            f"Invalid NIGHT buckets: "
            f"{night_invalid.height:,}"
        )

    print(
        f"OK - {result.height:,} buckets"
    )


def validate_session_counts(
    result: pl.DataFrame,
    timeframe: str,
) -> None:
    print(
        f"\n[7] SESSION COUNT - {timeframe}"
    )

    counts = (
        result
        .group_by("session")
        .len()
        .sort("session")
    )

    for row in counts.iter_rows():
        print(
            f"  {row[0]}: {row[1]:,}"
        )


def validate_symbol(symbol: str) -> None:
    print("\n" + "=" * 70)
    print(f"SYMBOL: {symbol}")
    print("=" * 70)

    df = load_1m_symbol(
        BASE_PATH,
        symbol,
    )

    print(
        f"1m rows: {df.height:,}"
    )

    print(
        f"date range: "
        f"{df['timestamp'].min()} "
        f"-> "
        f"{df['timestamp'].max()}"
    )

    validate_session(df)
    validate_day_boundaries(df)
    validate_night_boundaries(df)
    validate_ohlcv(df)
    validate_trade_date(df)

    for timeframe in TIMEFRAMES:
        result = aggregate_bars(
            df,
            timeframe,
        )

        validate_bucket(
            result,
            timeframe,
        )

        validate_session_counts(
            result,
            timeframe,
        )


def main() -> None:
    for symbol in SYMBOLS:
        validate_symbol(symbol)

    print("\n" + "=" * 70)
    print("ALL SESSION AGGREGATION VALIDATION PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()