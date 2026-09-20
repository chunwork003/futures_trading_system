from pathlib import Path

import polars as pl

from ingestion.bar_validation import validate_bars
from ingestion.github_txf_stream import iter_txf_sql_batches


def main():
    path = Path(
        "data/raw/github/txf/data_TXFR1_2026.sql"
    )

    batches = list(
        iter_txf_sql_batches(
            path,
            batch_size=100_000,
        )
    )

    df = pl.concat(batches)

    report = validate_bars(df)

    print("=" * 60)
    print("TXF 1m Validation Report")
    print("=" * 60)

    print(f"Rows:                 {report.rows:,}")
    print(f"Min timestamp:        {report.min_timestamp}")
    print(f"Max timestamp:        {report.max_timestamp}")
    print(f"Unique trade dates:   {report.unique_trade_dates:,}")
    print(f"Duplicate timestamps:  {report.duplicate_timestamp:,}")
    print(f"Null values:          {report.null_count:,}")
    print(f"Invalid OHLC:         {report.invalid_ohlc:,}")
    print(f"Negative volume:      {report.negative_volume:,}")
    print(f"Zero volume:          {report.zero_volume:,}")

    print()
    print("Contract:")
    print(
        df.group_by("contract")
        .len()
        .sort("len", descending=True)
    )

    print()
    print("Symbol:")
    print(
        df.group_by("symbol")
        .len()
        .sort("len", descending=True)
    )

    print()
    print("Source:")
    print(
        df.group_by("source")
        .len()
        .sort("len", descending=True)
    )

    print()
    print("Trade date sample:")
    print(
        df.group_by("trade_date")
        .len()
        .sort("trade_date")
        .head(10)
    )

    print()
    print("Trade date tail:")
    print(
        df.group_by("trade_date")
        .len()
        .sort("trade_date")
        .tail(10)
    )


if __name__ == "__main__":
    main()
