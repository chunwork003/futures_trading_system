from datetime import datetime
from pathlib import Path
import shutil

import polars as pl

from ingestion.github_txf_stream import iter_txf_sql_batches
from storage.canonical_parquet import CanonicalParquetWriter


SOURCE_PATH = Path(
    "data/raw/github/txf/data_TXFR1_2026.sql"
)

DATASET = "bar/1m"
SYMBOL = "TXF"

FINAL_ROOT = Path(
    "data/parquet/bar/1m/TXF"
)

STAGING_ROOT = Path(
    "data/staging/parquet/bar/1m/TXF"
)


def classify_one(timestamp: datetime) -> str:

    minute = (
        timestamp.hour * 60
        + timestamp.minute
    )

    if 8 * 60 + 45 <= minute < 13 * 60 + 45:
        return "DAY"

    if minute >= 15 * 60 or minute < 5 * 60:
        return "NIGHT"

    return "BREAK"


def classify_session(df: pl.DataFrame) -> pl.DataFrame:

    sessions = [
        classify_one(timestamp)
        for timestamp in df["timestamp"].to_list()
    ]

    return df.with_columns(
        pl.Series(
            "session",
            sessions,
        )
    )


def main():

    if not SOURCE_PATH.exists():
        raise FileNotFoundError(
            f"Source file not found: {SOURCE_PATH}"
        )

    if FINAL_ROOT.exists():
        shutil.rmtree(FINAL_ROOT)

    if STAGING_ROOT.exists():
        shutil.rmtree(STAGING_ROOT)

    writer = CanonicalParquetWriter()

    total_rows = 0
    total_parts = 0
    batch_id = 0

    for batch in iter_txf_sql_batches(
        SOURCE_PATH,
        batch_size=100_000,
    ):

        batch_id += 1

        batch = classify_session(batch)

        written = writer.write_batch(
            batch,
            dataset=DATASET,
            symbol=SYMBOL,
            batch_id=batch_id,
        )

        total_rows += batch.height
        total_parts += len(written)

        print(
            f"Batch {batch_id}: "
            f"{batch.height:,} rows | "
            f"{len(written)} part files"
        )

    print()
    print("Compacting part files...")

    final_files = writer.compact(
        dataset=DATASET,
        symbol=SYMBOL,
    )

    final_df = (
        writer.scan(
            dataset=DATASET,
            symbol=SYMBOL,
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
        .collect()
    )

    if final_df.height != total_rows:
        raise RuntimeError(
            "Parquet row count mismatch: "
            f"source={total_rows:,}, "
            f"final={final_df.height:,}"
        )

    print()
    print("=" * 70)
    print("Canonical Parquet Build Complete")
    print("=" * 70)
    print(f"Rows parsed:       {total_rows:,}")
    print(f"Part files:        {total_parts:,}")
    print(f"Final files:       {len(final_files):,}")

    print()
    print("Session distribution:")

    print(
        final_df
        .group_by("session")
        .agg(pl.len().alias("rows"))
        .sort("session")
    )

    if STAGING_ROOT.exists():
        shutil.rmtree(STAGING_ROOT)

    print()
    print("Staging cleaned.")


if __name__ == "__main__":
    main()
