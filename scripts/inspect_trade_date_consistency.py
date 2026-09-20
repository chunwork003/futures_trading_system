from pathlib import Path

import polars as pl

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

    df = pl.concat(batches).sort("timestamp")

    print("=" * 70)
    print("Timestamp / Trade Date Consistency")
    print("=" * 70)

    timestamp_range = df.select(
        [
            pl.col("timestamp").min().alias("min_timestamp"),
            pl.col("timestamp").max().alias("max_timestamp"),
        ]
    )

    print()
    print("Timestamp range:")
    print(timestamp_range)

    trade_date_range = df.select(
        [
            pl.col("trade_date").min().alias("min_trade_date"),
            pl.col("trade_date").max().alias("max_trade_date"),
        ]
    )

    print()
    print("Trade date range:")
    print(trade_date_range)

    mismatch = df.filter(
        pl.col("timestamp").dt.date()
        != pl.col("trade_date")
    )

    print()
    print(
        f"Timestamp date != trade_date: "
        f"{mismatch.height:,} rows"
    )

    if mismatch.height > 0:
        print()
        print("Mismatch sample:")
        print(
            mismatch.select(
                [
                    "timestamp",
                    "trade_date",
                    "contract",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                ]
            ).head(50)
        )

        print()
        print("Mismatch by timestamp date / trade date:")
        print(
            mismatch
            .with_columns(
                pl.col("timestamp")
                .dt.date()
                .alias("timestamp_date")
            )
            .group_by(
                [
                    "timestamp_date",
                    "trade_date",
                ]
            )
            .agg(
                [
                    pl.len().alias("rows"),
                    pl.col("timestamp").min().alias("first_timestamp"),
                    pl.col("timestamp").max().alias("last_timestamp"),
                ]
            )
            .sort(
                [
                    "timestamp_date",
                    "trade_date",
                ]
            )
            .head(100)
        )

    print()
    print("Last 30 rows:")
    print(
        df.select(
            [
                "timestamp",
                "trade_date",
                "contract",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ]
        ).tail(30)
    )

    print()
    print("Trade date distribution:")
    print(
        df.group_by("trade_date")
        .agg(
            [
                pl.len().alias("bars"),
                pl.col("timestamp")
                .min()
                .alias("first_timestamp"),
                pl.col("timestamp")
                .max()
                .alias("last_timestamp"),
            ]
        )
        .sort("trade_date")
        .tail(20)
    )


if __name__ == "__main__":
    main()
