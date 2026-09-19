from pathlib import Path

import polars as pl


BASE_PATH = Path("data/parquet/bar/1m")
OUTPUT_PATH = Path("data/parquet/bar")

SYMBOLS = ["TX", "MTX", "TMF"]
TIMEFRAMES = {
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "60m": 60,
}


def classify_session(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.when(
            (pl.col("timestamp").dt.time() >= pl.time(8, 45, 0))
            & (pl.col("timestamp").dt.time() < pl.time(13, 45, 0))
        )
        .then(pl.lit("DAY"))
        .when(
            (pl.col("timestamp").dt.time() >= pl.time(15, 0, 0))
            | (pl.col("timestamp").dt.time() < pl.time(5, 0, 0))
        )
        .then(pl.lit("NIGHT"))
        .otherwise(pl.lit("NONE"))
        .alias("session")
    )


def add_session_bucket(df: pl.DataFrame, minutes: int) -> pl.DataFrame:
    """
    建立以 Session 開始時間為基準的 bucket。

    DAY:
        08:45 起算

    NIGHT:
        15:00 起算，跨午夜仍屬同一 trade_date
    """

    return (
        df
        .with_columns(
            pl.when(pl.col("session") == "DAY")
            .then(
                (
                    (
                        pl.col("timestamp").dt.hour() * 60
                        + pl.col("timestamp").dt.minute()
                        - (8 * 60 + 45)
                    )
                    // minutes
                )
                .alias("bucket_index")
            )
            .when(pl.col("session") == "NIGHT")
            .then(
                (
                    (
                        pl.col("timestamp").dt.hour() * 60
                        + pl.col("timestamp").dt.minute()
                        + pl.when(
                            pl.col("timestamp").dt.hour() < 5
                        )
                        .then(24 * 60)
                        .otherwise(0)
                        - (15 * 60)
                    )
                    // minutes
                )
                .alias("bucket_index")
            )
            .otherwise(None)
        )
    )


def aggregate(df: pl.DataFrame, minutes: int) -> pl.DataFrame:
    df = classify_session(df)

    df = df.filter(
        pl.col("session").is_in(["DAY", "NIGHT"])
    )

    df = add_session_bucket(df, minutes)

    df = df.with_columns(
        pl.when(pl.col("session") == "DAY")
        .then(
            pl.datetime(
                pl.col("timestamp").dt.year(),
                pl.col("timestamp").dt.month(),
                pl.col("timestamp").dt.day(),
                8,
                45,
                0,
            )
            + pl.duration(
                minutes=pl.col("bucket_index") * minutes
            )
        )
        .otherwise(
            pl.when(
                pl.col("timestamp").dt.hour() >= 15
            )
            .then(
                pl.datetime(
                    pl.col("timestamp").dt.year(),
                    pl.col("timestamp").dt.month(),
                    pl.col("timestamp").dt.day(),
                    15,
                    0,
                    0,
                )
                + pl.duration(
                    minutes=pl.col("bucket_index") * minutes
                )
            )
            .otherwise(
                pl.datetime(
                    pl.col("timestamp").dt.year(),
                    pl.col("timestamp").dt.month(),
                    pl.col("timestamp").dt.day(),
                    15,
                    0,
                    0,
                )
                + pl.duration(
                    days=-1
                )
                + pl.duration(
                    minutes=pl.col("bucket_index") * minutes
                )
            )
        )
        .alias("timestamp")
    )

    result = (
        df
        .group_by(
            [
                "trade_date",
                "symbol",
                "contract",
                "timeframe",
                "session",
                "timestamp",
            ]
        )
        .agg(
            [
                pl.col("open").first().alias("open"),
                pl.col("high").max().alias("high"),
                pl.col("low").min().alias("low"),
                pl.col("close").last().alias("close"),
                pl.col("volume").sum().alias("volume"),
                pl.len().alias("trade_count"),
                pl.col("source").first().alias("source"),
            ]
        )
        .sort(["trade_date", "timestamp"])
    )

    return result


def process_symbol(symbol: str) -> None:
    input_path = BASE_PATH / symbol / "**/*.parquet"

    print(f"\n=== {symbol} ===")

    df = (
        pl.scan_parquet(str(input_path), hive_partitioning=True)
        .select(
            [
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
            ]
        )
        .collect()
    )

    print(f"1m rows: {df.height:,}")

    for timeframe, minutes in TIMEFRAMES.items():
        result = aggregate(df, minutes)

        output_dir = OUTPUT_PATH / timeframe / symbol
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = (
            output_dir
            / f"{symbol}_{timeframe}.parquet"
        )

        result.write_parquet(
            output_file,
            compression="zstd",
        )

        print(
            f"{timeframe}: "
            f"{result.height:,} rows -> "
            f"{output_file}"
        )


def main() -> None:
    for symbol in SYMBOLS:
        process_symbol(symbol)


if __name__ == "__main__":
    main()