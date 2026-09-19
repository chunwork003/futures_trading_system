from pathlib import Path

import polars as pl

from trading_calendar.trading_calendar import TradingCalendar
from trading_calendar.session_normalizer import SessionNormalizer


INPUT_BASE = Path("data/parquet/bar/1m")
OUTPUT_BASE = Path("data/parquet/bar/1m_normalized")

SYMBOLS = ["TX", "MTX", "TMF"]


def normalize_symbol(
    symbol: str,
    normalizer: SessionNormalizer,
) -> None:

    input_path = INPUT_BASE / symbol / "**/*.parquet"

    df = (
        pl.scan_parquet(
            str(input_path),
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
        .sort("timestamp")
    )

    print(f"{symbol}: input rows = {df.height:,}")

    result = normalizer.normalize(df)

    # 使用 normalized_trade_date 作為正式 trade_date
    result = (
        result
        .drop("trade_date")
        .rename({
            "normalized_trade_date": "trade_date",
        })
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
        .sort("timestamp")
    )

    output_dir = OUTPUT_BASE / symbol
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"{symbol}_1m_normalized.parquet"

    result.write_parquet(
        output_file,
        compression="zstd",
    )

    print(f"{symbol}: output rows = {result.height:,}")
    print(f"written: {output_file}")


def main():

    calendar = TradingCalendar(
        "database/market.duckdb"
    )

    normalizer = SessionNormalizer(calendar)

    for symbol in SYMBOLS:
        normalize_symbol(
            symbol,
            normalizer,
        )


if __name__ == "__main__":
    main()