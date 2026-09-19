import polars as pl


def resample_bars(
    df: pl.DataFrame,
    timeframe: str,
) -> pl.DataFrame:

    result = (
        df.sort("timestamp")
        .group_by_dynamic(
            index_column="timestamp",
            every=timeframe,
            group_by=[
                "symbol",
                "contract",
                "trade_date",
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
                pl.col("trade_count").sum().alias("trade_count"),
            ]
        )
        .with_columns(
            pl.lit(timeframe).alias("timeframe")
        )
    )

    return result