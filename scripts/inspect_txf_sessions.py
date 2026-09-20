from pathlib import Path

import polars as pl

from ingestion.github_txf_stream import iter_txf_sql_batches
from trading_calendar.session_resolver import (
    classify_session,
)


def main():
    path = Path(
        "data/raw/github/txf/data_TXFR1_2026.sql"
    )

    df = pl.concat(
        list(
            iter_txf_sql_batches(
                path,
                batch_size=100_000,
            )
        )
    ).sort("timestamp")

    df = df.with_columns(
        pl.col("timestamp")
        .map_elements(
            classify_session,
            return_dtype=pl.String,
        )
        .alias("expected_session")
    )

    print("=" * 70)
    print("TXF Session Analysis")
    print("=" * 70)

    print()
    print("Session distribution:")
    print(
        df.group_by("expected_session")
        .agg(pl.len().alias("rows"))
        .sort("expected_session")
    )

    print()
    print("Session + trade date distribution:")
    print(
        df.group_by(
            [
                "trade_date",
                "expected_session",
            ]
        )
        .agg(
            [
                pl.len().alias("bars"),
                pl.col("timestamp").min().alias("first_timestamp"),
                pl.col("timestamp").max().alias("last_timestamp"),
            ]
        )
        .sort("trade_date")
        .tail(20)
    )

    print()
    print("Break-session rows:")

    breaks = df.filter(
        pl.col("expected_session") == "BREAK"
    )

    print(f"Rows: {breaks.height:,}")

    if breaks.height > 0:
        print(breaks.head(50))


if __name__ == "__main__":
    main()
