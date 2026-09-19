from pathlib import Path

import polars as pl


ROOT = Path("data/parquet/bar")

TIMEFRAMES = ["5m", "15m", "30m", "60m"]


def validate_schema(df: pl.DataFrame, timeframe: str) -> None:
    expected = {
        "timestamp",
        "trade_date",
        "symbol",
        "contract",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "session",
        "timeframe",
        "source",
    }

    actual = set(df.columns)

    missing = expected - actual

    if missing:
        print(f"[FAIL] {timeframe} missing columns: {sorted(missing)}")
    else:
        print(f"[OK]   {timeframe} schema")


def validate_ohlc(df: pl.DataFrame, timeframe: str) -> None:
    invalid = df.filter(
        (pl.col("high") < pl.col("open"))
        | (pl.col("high") < pl.col("close"))
        | (pl.col("high") < pl.col("low"))
        | (pl.col("low") > pl.col("open"))
        | (pl.col("low") > pl.col("close"))
        | (pl.col("low") > pl.col("high"))
    )

    if invalid.height == 0:
        print(f"[OK]   {timeframe} OHLC")
    else:
        print(
            f"[FAIL] {timeframe} invalid OHLC: "
            f"{invalid.height}"
        )


def validate_duplicates(df: pl.DataFrame, timeframe: str) -> None:
    duplicated = (
        df.group_by(
            [
                "symbol",
                "trade_date",
                "session",
                "timestamp",
            ]
        )
        .len()
        .filter(pl.col("len") > 1)
    )

    if duplicated.height == 0:
        print(f"[OK]   {timeframe} duplicate")
    else:
        print(
            f"[FAIL] {timeframe} duplicate: "
            f"{duplicated.height}"
        )


def validate_trade_date_session(
    df: pl.DataFrame,
    timeframe: str,
) -> None:

    result = (
        df.group_by(
            [
                "symbol",
                "trade_date",
                "session",
            ]
        )
        .agg(
            [
                pl.col("timestamp").min().alias("first_timestamp"),
                pl.col("timestamp").max().alias("last_timestamp"),
                pl.len().alias("rows"),
            ]
        )
        .sort(
            [
                "symbol",
                "trade_date",
                "session",
            ]
        )
    )

    print(f"\n{timeframe} session summary:")
    print(result.head(20))


def validate_timeframe(
    df: pl.DataFrame,
    timeframe: str,
) -> None:

    print()
    print("=" * 60)
    print(f"TIMEFRAME: {timeframe}")
    print("=" * 60)

    print(f"rows: {df.height}")

    validate_schema(df, timeframe)
    validate_ohlc(df, timeframe)
    validate_duplicates(df, timeframe)

    print("\nSymbol counts:")

    print(
        df.group_by("symbol")
        .len()
        .sort("symbol")
    )

    print("\nDate range:")

    print(
        df.group_by("symbol")
        .agg(
            [
                pl.col("timestamp").min().alias("min_timestamp"),
                pl.col("timestamp").max().alias("max_timestamp"),
                pl.col("trade_date").min().alias("min_trade_date"),
                pl.col("trade_date").max().alias("max_trade_date"),
            ]
        )
        .sort("symbol")
    )

    validate_trade_date_session(df, timeframe)


def main() -> None:

    print("=== Aggregated Bar Validation ===")

    for timeframe in TIMEFRAMES:

        path = ROOT / timeframe / "bars.parquet"

        if not path.exists():
            print(f"[FAIL] Missing: {path}")
            continue

        df = pl.read_parquet(path)

        validate_timeframe(
            df,
            timeframe,
        )

    print()
    print("=== VALIDATION COMPLETE ===")


if __name__ == "__main__":
    main()