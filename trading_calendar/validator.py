import polars as pl


class TradingCalendarValidator:

    REQUIRED_COLUMNS = {
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

    def validate(
        self,
        df: pl.DataFrame,
    ) -> None:

        self._validate_columns(df)
        self._validate_dates(df)
        self._validate_sessions(df)

    def _validate_columns(
        self,
        df: pl.DataFrame,
    ) -> None:

        missing = (
            self.REQUIRED_COLUMNS
            - set(df.columns)
        )

        if missing:
            raise ValueError(
                f"Missing calendar columns: "
                f"{sorted(missing)}"
            )

    def _validate_dates(
        self,
        df: pl.DataFrame,
    ) -> None:

        if df["trade_date"].null_count() > 0:
            raise ValueError(
                "trade_date contains NULL values."
            )

        duplicate_count = (
            df
            .group_by("trade_date")
            .len()
            .filter(pl.col("len") > 1)
            .height
        )

        if duplicate_count > 0:
            raise ValueError(
                "Duplicate trade_date detected."
            )

    def _validate_sessions(
        self,
        df: pl.DataFrame,
    ) -> None:

        invalid_day = df.filter(
            (~pl.col("is_trading_day"))
            & pl.col("day_session")
        ).height

        if invalid_day > 0:
            raise ValueError(
                "Non-trading days cannot have "
                "day_session=True."
            )

        invalid_night = df.filter(
            (~pl.col("is_trading_day"))
            & pl.col("night_session")
        ).height

        if invalid_night > 0:
            raise ValueError(
                "Non-trading days cannot have "
                "night_session=True."
            )