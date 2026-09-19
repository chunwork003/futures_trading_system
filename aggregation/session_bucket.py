from __future__ import annotations

from datetime import date, datetime, time, timedelta

import polars as pl


DAY_OPEN = time(8, 45)
DAY_CLOSE = time(13, 45)

NIGHT_OPEN = time(15, 0)
NIGHT_CLOSE = time(5, 0)


def get_session_anchor(
    trade_date: date,
    session: str,
) -> datetime:
    """
    回傳該交易 Session 的起始時間。

    DAY:
        trade_date 08:45

    NIGHT:
        trade_date 前一日 15:00

    注意：
    NIGHT 的 trade_date 是「實際交易日」，
    不是 timestamp 的 calendar date。
    """
    if session == "DAY":
        return datetime.combine(trade_date, DAY_OPEN)

    if session == "NIGHT":
        return datetime.combine(
            trade_date - timedelta(days=1),
            NIGHT_OPEN,
        )

    raise ValueError(f"Unsupported session: {session}")


def calculate_bucket_start(
    timestamp: datetime,
    trade_date: date,
    session: str,
    timeframe_minutes: int,
) -> datetime:
    """
    計算單筆 K 線所屬的 Session bucket 起始時間。
    """

    if timeframe_minutes <= 0:
        raise ValueError("timeframe_minutes must be > 0")

    anchor = get_session_anchor(
        trade_date=trade_date,
        session=session,
    )

    elapsed_seconds = int(
        (timestamp - anchor).total_seconds()
    )

    bucket_seconds = timeframe_minutes * 60

    bucket_index = elapsed_seconds // bucket_seconds

    return anchor + timedelta(
        seconds=bucket_index * bucket_seconds
    )


def add_bucket_start(
    df: pl.DataFrame,
    timeframe_minutes: int,
) -> pl.DataFrame:
    """
    對 DataFrame 新增 bucket_start。

    必須存在：
        timestamp
        trade_date
        session
    """

    required_columns = {
        "timestamp",
        "trade_date",
        "session",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if timeframe_minutes <= 0:
        raise ValueError(
            "timeframe_minutes must be > 0"
        )

    # DAY anchor:
    #   trade_date 08:45
    #
    # NIGHT anchor:
    #   trade_date 前一天 15:00
    #
    # 使用 trade_date，而不是 timestamp.date()，
    # 是跨午夜 NIGHT 正確處理的關鍵。

    trade_date_datetime = (
        pl.col("trade_date")
        .cast(pl.Datetime("us"))
    )

    day_anchor = (
        trade_date_datetime
        + pl.duration(hours=8, minutes=45)
    )

    night_anchor = (
        trade_date_datetime
        + pl.duration(days=-1, hours=15)
    )

    anchor = (
        pl.when(pl.col("session") == "DAY")
        .then(day_anchor)
        .when(pl.col("session") == "NIGHT")
        .then(night_anchor)
        .otherwise(None)
        .alias("_session_anchor")
    )

    result = (
        df
        .with_columns(anchor)
        .with_columns(
            (
                (
                    pl.col("timestamp")
                    - pl.col("_session_anchor")
                ).dt.total_seconds()
                // (timeframe_minutes * 60)
            ).alias("_bucket_index")
        )
        .with_columns(
            (
                pl.col("_session_anchor")
                + pl.duration(
                    seconds=(
                        pl.col("_bucket_index")
                        * timeframe_minutes
                        * 60
                    )
                )
            ).alias("bucket_start")
        )
        .drop(
            [
                "_session_anchor",
                "_bucket_index",
            ]
        )
    )

    return result