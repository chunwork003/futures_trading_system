from pathlib import Path

import polars as pl

from ingestion.github_txf_stream import iter_txf_sql_batches
from trading_calendar.session_resolver import SessionResolver
from trading_calendar.trading_calendar import TradingCalendar


DATA_PATH = Path(
    "data/raw/github/txf/data_TXFR1_2026.sql"
)


def load_data() -> pl.DataFrame:
    return pl.concat(
        list(
            iter_txf_sql_batches(
                DATA_PATH,
                batch_size=100_000,
            )
        )
    ).sort("timestamp")


def classify_session_vectorized(df: pl.DataFrame) -> pl.DataFrame:

    minute_of_day = (
        pl.col("timestamp").dt.hour() * 60
        + pl.col("timestamp").dt.minute()
    )

    return df.with_columns(
        pl.when(
            (minute_of_day >= 8 * 60 + 45)
            & (minute_of_day < 13 * 60 + 45)
        )
        .then(pl.lit("DAY"))
        .when(
            (minute_of_day >= 15 * 60)
            | (minute_of_day < 5 * 60)
        )
        .then(pl.lit("NIGHT"))
        .otherwise(pl.lit("BREAK"))
        .alias("calculated_session")
    )


def main():

    df = load_data()

    print("=" * 70)
    print("TXF 1m Corrected Data Validation")
    print("=" * 70)

    print()
    print(f"Rows: {df.height:,}")

    # ---------------------------------------------------------
    # 1. Session classification
    # ---------------------------------------------------------

    print()
    print("-" * 70)
    print("1. Session Classification")
    print("-" * 70)

    df = classify_session_vectorized(df)

    print(
        df.group_by("calculated_session")
        .agg(pl.len().alias("rows"))
        .sort("calculated_session")
    )

    # ---------------------------------------------------------
    # 2. BREAK rows
    # ---------------------------------------------------------

    print()
    print("-" * 70)
    print("2. BREAK Rows")
    print("-" * 70)

    breaks = df.filter(
        pl.col("calculated_session") == "BREAK"
    )

    print(
        f"BREAK rows: {breaks.height:,}"
    )

    if breaks.height:
        print(
            breaks.select(
                [
                    "timestamp",
                    "trade_date",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                ]
            )
        )

    # ---------------------------------------------------------
    # 3. Zero volume
    # ---------------------------------------------------------

    print()
    print("-" * 70)
    print("3. Zero Volume")
    print("-" * 70)

    zero = df.filter(
        pl.col("volume") == 0
    )

    print(
        f"Zero-volume rows: {zero.height:,}"
    )

    if zero.height:
        print()
        print(
            zero.group_by(
                "calculated_session"
            )
            .agg(
                pl.len().alias("rows")
            )
            .sort("calculated_session")
        )

        print()
        print("Zero-volume sample:")

        print(
            zero.select(
                [
                    "timestamp",
                    "trade_date",
                    "calculated_session",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                ]
            ).head(50)
        )

    # ---------------------------------------------------------
    # 4. Per trade_date / session bar counts
    # ---------------------------------------------------------

    print()
    print("-" * 70)
    print("4. Trade Date / Session Bar Counts")
    print("-" * 70)

    session_counts = (
        df.filter(
            pl.col("calculated_session")
            != "BREAK"
        )
        .group_by(
            [
                "trade_date",
                "calculated_session",
            ]
        )
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
        .sort(
            [
                "trade_date",
                "calculated_session",
            ]
        )
    )

    print(
        "Expected DAY bars:   300"
    )
    print(
        "Expected NIGHT bars: 840"
    )

    print()
    print("Abnormal session counts:")

    abnormal = session_counts.filter(
        (
            (
                pl.col("calculated_session") == "DAY"
            )
            & (pl.col("bars") != 300)
        )
        |
        (
            (
                pl.col("calculated_session") == "NIGHT"
            )
            & (pl.col("bars") != 840)
        )
    )

    print(
        f"Abnormal session groups: "
        f"{abnormal.height:,}"
    )

    if abnormal.height:
        print(abnormal.head(100))

    # ---------------------------------------------------------
    # 5. Missing minutes inside each session
    # ---------------------------------------------------------

    print()
    print("-" * 70)
    print("5. Missing Minutes Inside Sessions")
    print("-" * 70)

    session_gap_results = []

    for group in session_counts.iter_rows(named=True):

        trade_date = group["trade_date"]
        session = group["calculated_session"]

        session_df = df.filter(
            (
                pl.col("trade_date")
                == trade_date
            )
            &
            (
                pl.col("calculated_session")
                == session
            )
        ).sort("timestamp")

        if session_df.height <= 1:
            continue

        gaps = (
            session_df
            .with_columns(
                pl.col("timestamp")
                .diff()
                .alias("delta")
            )
            .filter(
                pl.col("delta")
                > pl.duration(minutes=1)
            )
        )

        if gaps.height:
            session_gap_results.append(
                {
                    "trade_date": trade_date,
                    "session": session,
                    "bars": session_df.height,
                    "gap_count": gaps.height,
                    "largest_gap": gaps["delta"].max(),
                }
            )

    if session_gap_results:

        gap_df = pl.DataFrame(
            session_gap_results
        ).sort(
            "largest_gap",
            descending=True,
        )

        print(
            f"Sessions containing gaps: "
            f"{gap_df.height:,}"
        )

        print(
            gap_df.head(100)
        )

    else:
        print(
            "No internal session gaps detected."
        )

    # ---------------------------------------------------------
    # 6. Existing SessionResolver samples
    # ---------------------------------------------------------

    print()
    print("-" * 70)
    print("6. Existing SessionResolver Samples")
    print("-" * 70)

    calendar = TradingCalendar(
        "database/market.duckdb"
    )

    resolver = SessionResolver(calendar)

    sample_timestamps = [
        # Known session boundaries
        df["timestamp"].min(),
        df["timestamp"].max(),

        # Known boundary rows
        *(
            breaks["timestamp"]
            .to_list()
            if breaks.height
            else []
        ),

        # Typical timestamps
        df.filter(
            pl.col("timestamp")
            .dt.hour()
            == 8
        )["timestamp"].head(1).to_list()[0],

        df.filter(
            pl.col("timestamp")
            .dt.hour()
            == 15
        )["timestamp"].head(1).to_list()[0],
    ]

    for timestamp in sample_timestamps:

        result = resolver.resolve(timestamp)

        print(
            timestamp,
            "=>",
            result.session_type,
            result.trade_date,
            "trading=",
            result.is_trading,
        )

    print()
    print("=" * 70)
    print("Corrected Validation Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
