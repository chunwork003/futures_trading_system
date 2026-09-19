from pathlib import Path

import duckdb
import polars as pl

from trading_calendar.validator import TradingCalendarValidator


class TradingCalendarLoader:

    def __init__(
        self,
        database_path: str = "database/market.duckdb",
    ):
        self.database_path = Path(database_path)

    def load_dataframe(
        self,
        df: pl.DataFrame,
    ) -> None:

        calendar_validator = TradingCalendarValidator()
        calendar_validator.validate(df)

        required_columns = {
            "trade_date",
            "is_trading_day",
            "day_session",
            "night_session",
            "day_open",
            "day_close",
            "night_open",
            "night_close",
            "notes",
        }

        missing = required_columns - set(df.columns)

        if missing:
            raise ValueError(
                f"Missing columns: {sorted(missing)}"
            )

        conn = duckdb.connect(
            str(self.database_path)
        )

        try:
            conn.register(
                "calendar_df",
                df.to_arrow(),
            )

            conn.execute(
                """
                INSERT OR REPLACE INTO trading_calendar (
                    trade_date,
                    is_trading_day,
                    day_session,
                    night_session,
                    day_open,
                    day_close,
                    night_open,
                    night_close,
                    notes
                )
                SELECT
                    trade_date,
                    is_trading_day,
                    day_session,
                    night_session,
                    day_open,
                    day_close,
                    night_open,
                    night_close,
                    notes
                FROM calendar_df
                """
            )

        finally:
            conn.close()