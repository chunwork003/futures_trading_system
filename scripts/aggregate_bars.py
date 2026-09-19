from pathlib import Path

import polars as pl


INPUT_ROOT = Path("data/parquet/bar/1m")
OUTPUT_ROOT = Path("data/parquet/bar")


TIMEFRAMES = {
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "60m": "60m",
}


def aggregate_timeframe(
    timeframe: str,
    every: str,
) -> None:

    print(f"Aggregating {timeframe}...")

    df = (
        pl.scan_parquet(
            str(INPUT_ROOT / "**/*.parquet"),
            hive_partitioning=True,
        )
        .select(
            [
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
                "source",
            ]
        )
        .sort(
            [
                "symbol",
                "trade_date",
                "timestamp",
            ]
        )
    )

    result = (
        df.group_by_dynamic(
            index_column="timestamp",
            every=every,
            period=every,
            group_by=[
                "symbol",
                "trade_date",
                "contract",
                "session",
            ],
            closed="left",
            label="left",
        )
        .agg(
            [
                pl.col("open").first().alias("open"),
                pl.col("high").max().alias("high"),
                pl.col("low").min().alias("low"),
                pl.col("close").last().alias("close"),
                pl.col("volume").sum().alias("volume"),
                pl.lit(timeframe).alias("timeframe"),
                pl.col("source").first().alias("source"),
            ]
        )
        .filter(
            pl.col("open").is_not_null()
        )
        .collect()
        .sort(
            [
                "symbol",
                "trade_date",
                "timestamp",
            ]
        )
    )

    output_dir = OUTPUT_ROOT / timeframe
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "bars.parquet"

    result.write_parquet(
        output_path,
        compression="zstd",
    )

    print(f"  rows: {result.height}")
    print(f"  output: {output_path}")


def main() -> None:

    for timeframe, every in TIMEFRAMES.items():
        aggregate_timeframe(
            timeframe,
            every,
        )

    print()
    print("Aggregation complete.")


if __name__ == "__main__":
    main()