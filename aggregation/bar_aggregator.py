from __future__ import annotations

from pathlib import Path

import polars as pl

from aggregation.session_bucket import add_bucket_start


TIMEFRAMES = {
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "60m": 60,
}


REQUIRED_COLUMNS = {
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
}


def aggregate_bars(
    df: pl.DataFrame,
    timeframe: str,
) -> pl.DataFrame:
    """
    將 canonical 1m bars 聚合成指定 timeframe。

    前提：
        timestamp
        trade_date
        symbol
        contract
        session
        OHLCV

    已經是 canonical schema。
    """

    if timeframe not in TIMEFRAMES:
        raise ValueError(
            f"Unsupported timeframe: {timeframe}"
        )

    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    minutes = TIMEFRAMES[timeframe]

    # 只允許真正的交易 Session
    df = df.filter(
        pl.col("session").is_in(
            ["DAY", "NIGHT"]
        )
    )

    if df.is_empty():
        return df

    # 建立 Session-aware bucket
    df = add_bucket_start(
        df,
        timeframe_minutes=minutes,
    )

    # 統一 timeframe
    df = df.with_columns(
        pl.lit(timeframe).alias("timeframe")
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
                "bucket_start",
            ]
        )
        .agg(
            [
                pl.col("open")
                .first()
                .alias("open"),

                pl.col("high")
                .max()
                .alias("high"),

                pl.col("low")
                .min()
                .alias("low"),

                pl.col("close")
                .last()
                .alias("close"),

                pl.col("volume")
                .sum()
                .alias("volume"),

                pl.len()
                .alias("trade_count"),

                pl.col("source")
                .first()
                .alias("source"),
            ]
        )
        .rename(
            {
                "bucket_start": "timestamp",
            }
        )
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
                "trade_count",
                "session",
                "source",
            ]
        )
        .sort(
            [
                "trade_date",
                "session",
                "timestamp",
            ]
        )
    )

    return result


def aggregate_all(
    df: pl.DataFrame,
) -> dict[str, pl.DataFrame]:
    """
    一次產生 5m / 15m / 30m / 60m。
    """

    return {
        timeframe: aggregate_bars(
            df,
            timeframe,
        )
        for timeframe in TIMEFRAMES
    }


def load_1m_symbol(
    base_path: str,
    symbol: str,
) -> pl.DataFrame:
    """
    讀取指定商品的 canonical 1m Parquet。
    """

    path = (
        Path(base_path)
        / symbol
        / "**/*.parquet"
    )

    return (
        pl.scan_parquet(
            str(path),
            hive_partitioning=True,
        )
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


def write_timeframe(
    df: pl.DataFrame,
    output_base: str,
    timeframe: str,
    symbol: str,
) -> Path:

    output_dir = (
        Path(output_base)
        / timeframe
        / symbol
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_dir
        / f"{symbol}_{timeframe}.parquet"
    )

    df.write_parquet(
        output_file,
        compression="zstd",
    )

    return output_file