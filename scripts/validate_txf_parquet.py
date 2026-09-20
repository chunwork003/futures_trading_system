from pathlib import Path

import polars as pl

from storage.canonical_parquet import (
    CanonicalParquetWriter,
    CANONICAL_COLUMNS,
)


def main():

    root = Path(
        "data/parquet/bar/1m/TXF"
    )

    if not root.exists():
        raise FileNotFoundError(
            f"Parquet dataset not found: {root}"
        )

    files = sorted(
        root.rglob("*.parquet")
    )

    print("=" * 70)
    print("TXF Canonical Parquet Validation")
    print("=" * 70)

    print()
    print(f"Parquet files: {len(files):,}")

    writer = CanonicalParquetWriter()

    df = (
        writer.scan(
            dataset="bar/1m",
            symbol="TXF",
        )
        .select(CANONICAL_COLUMNS)
        .collect()
        .sort("timestamp")
    )

    print()
    print(f"Rows: {df.height:,}")

    print()
    print("Schema:")
    print(df.schema)

    print()
    print("Time range:")
    print(
        df.select(
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

    print()
    print("Trade date range:")
    print(
        df.select(
            [
                pl.col("trade_date")
                .min()
                .alias("min_trade_date"),
                pl.col("trade_date")
                .max()
                .alias("max_trade_date"),
            ]
        )
    )

    print()
    print("Source:")
    print(
        df.group_by("source")
        .agg(pl.len().alias("rows"))
        .sort("source")
    )

    print()
    print("Symbol:")
    print(
        df.group_by("symbol")
        .agg(pl.len().alias("rows"))
        .sort("symbol")
    )

    print()
    print("Duplicate keys:")

    duplicates = (
        df.group_by(
            [
                "timestamp",
                "symbol",
                "contract",
                "timeframe",
            ]
        )
        .len()
        .filter(pl.col("len") > 1)
    )

    print(duplicates.height)

    print()
    print("Canonical columns:")
    print(df.columns)

    if df.columns != CANONICAL_COLUMNS:
        raise AssertionError(
            f"Unexpected columns: {df.columns}"
        )

    if df.height != 185_420:
        raise AssertionError(
            f"Unexpected row count: {df.height}"
        )

    if duplicates.height != 0:
        raise AssertionError(
            "Duplicate canonical bars detected"
        )

    print()
    print("=" * 70)
    print("Parquet Validation PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()
