import polars as pl


def tick_to_1m(df: pl.DataFrame) -> pl.DataFrame:

    result = (
        df.sort("timestamp")
        .group_by_dynamic(
            index_column="timestamp",
            every="1m",
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
                pl.col("price").first().alias("open"),
                pl.col("price").max().alias("high"),
                pl.col("price").min().alias("low"),
                pl.col("price").last().alias("close"),
                pl.col("volume").sum().alias("volume"),
                pl.len().alias("trade_count"),
            ]
        )
        .with_columns(
            pl.lit("1m").alias("timeframe")
        )
        .sort(
            [
                "symbol",
                "contract",
                "timestamp",
            ]
        )
    )

    return result