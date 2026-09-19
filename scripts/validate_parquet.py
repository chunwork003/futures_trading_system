from pathlib import Path

import polars as pl


PARQUET_ROOT = Path("data/parquet/bar/1m")


def main():
    print("=== Canonical 1m Parquet Validation ===")
    print()

    files = list(PARQUET_ROOT.glob("**/*.parquet"))

    if not files:
        raise FileNotFoundError(
            f"No parquet files found: {PARQUET_ROOT}"
        )

    print(f"Parquet files: {len(files)}")
    print()

    df = pl.scan_parquet(
        str(PARQUET_ROOT / "**/*.parquet"),
        hive_partitioning=True,
    )

    # --------------------------------------------------
    # 1. Schema
    # --------------------------------------------------
    print("1. SCHEMA")

    schema = df.collect_schema()

    for name, dtype in schema.items():
        print(f"{name}: {dtype}")

    print()

    # --------------------------------------------------
    # 2. Row count
    # --------------------------------------------------
    print("2. ROW COUNT")

    result = (
        df.group_by("symbol")
        .agg(pl.len().alias("rows"))
        .sort("symbol")
        .collect()
    )

    print(result)
    print()

    # --------------------------------------------------
    # 3. Symbol
    # --------------------------------------------------
    print("3. SYMBOL")

    symbols = (
        df.select("symbol")
        .unique()
        .sort("symbol")
        .collect()
    )

    print(symbols)
    print()

    # --------------------------------------------------
    # 4. Duplicate
    # --------------------------------------------------
    print("4. DUPLICATE")

    duplicates = (
        df.group_by(["symbol", "timestamp"])
        .len()
        .filter(pl.col("len") > 1)
        .collect()
    )

    if duplicates.height == 0:
        print("OK - no duplicate (symbol, timestamp)")
    else:
        print("FOUND DUPLICATES:")
        print(duplicates.head(20))

    print()

    # --------------------------------------------------
    # 5. OHLC
    # --------------------------------------------------
    print("5. OHLC VALIDATION")

    invalid_ohlc = (
        df.filter(
            (pl.col("high") < pl.col("low"))
            | (pl.col("high") < pl.col("open"))
            | (pl.col("high") < pl.col("close"))
            | (pl.col("low") > pl.col("open"))
            | (pl.col("low") > pl.col("close"))
        )
        .collect()
    )

    if invalid_ohlc.height == 0:
        print("OK - no invalid OHLC rows")
    else:
        print("FOUND INVALID OHLC:")
        print(invalid_ohlc.head(20))

    print()

    # --------------------------------------------------
    # 6. Negative volume
    # --------------------------------------------------
    print("6. NEGATIVE VOLUME")

    negative_volume = (
        df.filter(pl.col("volume") < 0)
        .collect()
    )

    if negative_volume.height == 0:
        print("OK - no negative volume")
    else:
        print("FOUND NEGATIVE VOLUME:")
        print(negative_volume.head(20))

    print()

    # --------------------------------------------------
    # 7. NULL
    # --------------------------------------------------
    print("7. NULL CHECK")

    nulls = (
        df.select(
            [
                pl.col("timestamp").null_count().alias("timestamp"),
                pl.col("trade_date").null_count().alias("trade_date"),
                pl.col("symbol").null_count().alias("symbol"),
                pl.col("contract").null_count().alias("contract"),
                pl.col("open").null_count().alias("open"),
                pl.col("high").null_count().alias("high"),
                pl.col("low").null_count().alias("low"),
                pl.col("close").null_count().alias("close"),
                pl.col("volume").null_count().alias("volume"),
            ]
        )
        .collect()
    )

    print(nulls)
    print()

    # --------------------------------------------------
    # 8. Date range
    # --------------------------------------------------
    print("8. DATE RANGE")

    date_range = (
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
        .collect()
    )

    print(date_range)
    print()

    # --------------------------------------------------
    # 9. Contract mapping
    # --------------------------------------------------
    print("9. CONTRACT MAPPING")

    mapping = (
        df.group_by(["symbol", "contract"])
        .agg(pl.len().alias("rows"))
        .sort(["symbol", "contract"])
        .collect()
    )

    print(mapping)
    print()

    # --------------------------------------------------
    # 10. Timeframe
    # --------------------------------------------------
    print("10. TIMEFRAME")

    timeframes = (
        df.select("timeframe")
        .unique()
        .sort("timeframe")
        .collect()
    )

    print(timeframes)
    print()

    # --------------------------------------------------
    # 11. Source
    # --------------------------------------------------
    print("11. SOURCE")

    sources = (
        df.select("source")
        .unique()
        .sort("source")
        .collect()
    )

    print(sources)
    print()

    print("=== VALIDATION COMPLETE ===")


if __name__ == "__main__":
    main()