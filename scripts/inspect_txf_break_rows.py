from pathlib import Path

import polars as pl

from storage.canonical_parquet import (
    CanonicalParquetWriter,
)


DATABASE_PATH = Path(
    "database/market.duckdb"
)


def main():

    writer = CanonicalParquetWriter()

    df = (
        writer.scan(
            dataset="bar/1m",
            symbol="TXF",
        )
        .select([
            "timestamp",
            "trade_date",
            "symbol",
            "contract",
            "timeframe",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "session",
            "source",
        ])
        .filter(
            pl.col("session") == "BREAK"
        )
        .collect()
        .sort("timestamp")
    )

    print("=" * 80)
    print("TXF 1m BREAK Row Inspection")
    print("=" * 80)

    print()
    print(f"BREAK rows: {df.height}")

    print()

    if df.is_empty():
        print("No BREAK rows found.")
        return

    print(
        df.to_pandas().to_string(
            index=False
        )
    )

    print()
    print("BREAK timestamp distribution:")

    print(
        df.group_by(
            pl.col("timestamp").dt.strftime("%H:%M")
        )
        .agg(
            pl.len().alias("rows"),
            pl.col("volume").sum().alias("volume"),
        )
        .sort("timestamp")
    )

    print()
    print("BREAK trade dates:")

    print(
        df.select([
            "timestamp",
            "trade_date",
            "volume",
            "open",
            "high",
            "low",
            "close",
        ])
    )


if __name__ == "__main__":
    main()
