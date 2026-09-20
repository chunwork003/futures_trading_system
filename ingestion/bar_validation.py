from dataclasses import dataclass

import polars as pl


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
}


@dataclass(frozen=True)
class BarValidationReport:
    rows: int
    min_timestamp: object
    max_timestamp: object
    unique_trade_dates: int
    duplicate_timestamp: int
    null_count: int
    invalid_ohlc: int
    negative_volume: int
    zero_volume: int


def validate_bars(df: pl.DataFrame) -> BarValidationReport:
    missing = REQUIRED_COLUMNS - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}"
        )

    required_columns = sorted(REQUIRED_COLUMNS)

    null_count = (
        df.select(
            [
                pl.col(column).null_count().alias(column)
                for column in required_columns
            ]
        )
        .sum_horizontal()
        .item()
    )

    duplicate_timestamp = (
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
        .height
    )

    invalid_ohlc = df.filter(
        (pl.col("high") < pl.max_horizontal(
            "open",
            "close",
            "low",
        ))
        |
        (pl.col("low") > pl.min_horizontal(
            "open",
            "close",
            "high",
        ))
    ).height

    negative_volume = df.filter(
        pl.col("volume") < 0
    ).height

    zero_volume = df.filter(
        pl.col("volume") == 0
    ).height

    return BarValidationReport(
        rows=df.height,
        min_timestamp=df["timestamp"].min(),
        max_timestamp=df["timestamp"].max(),
        unique_trade_dates=df["trade_date"].n_unique(),
        duplicate_timestamp=duplicate_timestamp,
        null_count=null_count,
        invalid_ohlc=invalid_ohlc,
        negative_volume=negative_volume,
        zero_volume=zero_volume,
    )
