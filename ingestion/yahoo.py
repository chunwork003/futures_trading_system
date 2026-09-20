from datetime import date, timedelta

import polars as pl
import yfinance as yf

from ingestion.base import DataSource
from ingestion.yahoo_config import get_interval_policy, get_symbol_config


CANONICAL_COLUMNS = [
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


class YahooDataSource(DataSource):
    @property
    def source_name(self) -> str:
        return "yahoo"

    def download(
        self,
        start_date: date,
        end_date: date,
        symbol: str = "TXF",
        timeframe: str = "1m",
    ) -> pl.DataFrame:
        if start_date > end_date:
            raise ValueError("start_date must be <= end_date")

        config = get_symbol_config(symbol)
        get_interval_policy(timeframe)

        request_end = end_date + timedelta(days=1)

        df = yf.download(
            tickers=config.yahoo_symbol,
            start=start_date.isoformat(),
            end=request_end.isoformat(),
            interval=timeframe,
            auto_adjust=False,
            actions=False,
            progress=False,
            prepost=False,
            threads=False,
        )

        if df is None or df.empty:
            return self._empty()

        return self._normalize(
            df=df,
            canonical_symbol=config.canonical_symbol,
            yahoo_symbol=config.yahoo_symbol,
            timeframe=timeframe,
            timezone=config.timezone,
        )

    @staticmethod
    def _empty() -> pl.DataFrame:
        return pl.DataFrame(
            {
                "timestamp": pl.Series([], dtype=pl.Datetime("us")),
                "trade_date": pl.Series([], dtype=pl.Date),
                "symbol": pl.Series([], dtype=pl.String),
                "contract": pl.Series([], dtype=pl.String),
                "timeframe": pl.Series([], dtype=pl.String),
                "open": pl.Series([], dtype=pl.Float64),
                "high": pl.Series([], dtype=pl.Float64),
                "low": pl.Series([], dtype=pl.Float64),
                "close": pl.Series([], dtype=pl.Float64),
                "volume": pl.Series([], dtype=pl.Int64),
                "session": pl.Series([], dtype=pl.String),
                "source": pl.Series([], dtype=pl.String),
            }
        )

    @staticmethod
    def _normalize(
        df,
        canonical_symbol: str,
        yahoo_symbol: str,
        timeframe: str,
        timezone: str,
    ) -> pl.DataFrame:
        # yfinance may return MultiIndex columns even for one ticker.
        if hasattr(df.columns, "levels"):
            try:
                df = df.xs(yahoo_symbol, axis=1, level=1)
            except Exception:
                try:
                    df.columns = df.columns.get_level_values(0)
                except Exception:
                    pass

        required = ["Open", "High", "Low", "Close", "Volume"]
        missing = [column for column in required if column not in df.columns]

        if missing:
            raise ValueError(
                f"Yahoo response missing columns: {missing}; "
                f"columns={list(df.columns)}"
            )

        # Normalize pandas DatetimeIndex.
        timestamps = df.index

        if getattr(timestamps, "tz", None) is not None:
            timestamps = timestamps.tz_convert(timezone).tz_localize(None)

        # Explicitly convert every timestamp to native Python datetime.
        # This prevents Polars from inferring an Object column.
        timestamp_values = [
            value.to_pydatetime()
            if hasattr(value, "to_pydatetime")
            else value
            for value in timestamps
        ]

        normalized = pl.DataFrame(
            {
                "timestamp": pl.Series(
                    "timestamp",
                    timestamp_values,
                    dtype=pl.Datetime("us"),
                ),
                "open": pl.Series(
                    "open",
                    df["Open"].astype(float).to_numpy(),
                    dtype=pl.Float64,
                ),
                "high": pl.Series(
                    "high",
                    df["High"].astype(float).to_numpy(),
                    dtype=pl.Float64,
                ),
                "low": pl.Series(
                    "low",
                    df["Low"].astype(float).to_numpy(),
                    dtype=pl.Float64,
                ),
                "close": pl.Series(
                    "close",
                    df["Close"].astype(float).to_numpy(),
                    dtype=pl.Float64,
                ),
                "volume": pl.Series(
                    "volume",
                    df["Volume"].fillna(0).astype("int64").to_numpy(),
                    dtype=pl.Int64,
                ),
            }
        )

        return (
            normalized
            .with_columns(
                [
                    pl.col("timestamp").dt.date().alias("trade_date"),
                    pl.lit(canonical_symbol).alias("symbol"),
                    pl.lit(yahoo_symbol).alias("contract"),
                    pl.lit(timeframe).alias("timeframe"),
                    pl.lit(None, dtype=pl.String).alias("session"),
                    pl.lit("yahoo").alias("source"),
                ]
            )
            .select(CANONICAL_COLUMNS)
            .sort("timestamp")
        )
