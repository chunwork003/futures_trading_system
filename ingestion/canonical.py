from datetime import date

import polars as pl


def filter_date_range(
    df: pl.DataFrame,
    start_date: date,
    end_date: date,
) -> pl.DataFrame:
    """Filter canonical bars by trade date, inclusive."""

    if start_date > end_date:
        raise ValueError("start_date must be <= end_date")

    return df.filter(
        pl.col("trade_date").is_between(
            start_date,
            end_date,
            closed="both",
        )
    )


def validate_canonical_bars(df: pl.DataFrame) -> None:
    """Validate basic canonical OHLCV invariants."""

    required = {
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
        "source",
    }

    missing = required.difference(df.columns)

    if missing:
        raise ValueError(
            f"Missing canonical columns: {sorted(missing)}"
        )

    if df.is_empty():
        return

    if df["timestamp"].null_count() > 0:
        raise ValueError("timestamp contains null values")

    if df["trade_date"].null_count() > 0:
        raise ValueError("trade_date contains null values")

    if df["open"].null_count() > 0:
        raise ValueError("open contains null values")

    if df["high"].null_count() > 0:
        raise ValueError("high contains null values")

    if df["low"].null_count() > 0:
        raise ValueError("low contains null values")

    if df["close"].null_count() > 0:
        raise ValueError("close contains null values")

    if df["volume"].null_count() > 0:
        raise ValueError("volume contains null values")

    invalid_ohlc = df.filter(
        (pl.col("high") < pl.max_horizontal("open", "close", "low"))
        | (pl.col("low") > pl.min_horizontal("open", "close", "high"))
    )

    if not invalid_ohlc.is_empty():
        raise ValueError(
            f"Invalid OHLC rows: {invalid_ohlc.height}"
        )

    if (df["volume"] < 0).any():
        raise ValueError("volume contains negative values")
