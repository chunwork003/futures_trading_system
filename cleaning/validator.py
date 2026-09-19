from datetime import date
from typing import Optional

import polars as pl


class ValidationResult:
    """
    Data validation result.
    """

    def __init__(
        self,
        valid: bool,
        errors: Optional[list[str]] = None,
        warnings: Optional[list[str]] = None,
    ):
        self.valid = valid
        self.errors = errors or []
        self.warnings = warnings or []

    def __repr__(self) -> str:
        return (
            f"ValidationResult("
            f"valid={self.valid}, "
            f"errors={len(self.errors)}, "
            f"warnings={len(self.warnings)}"
            f")"
        )


class DataValidator:
    """
    Validate market data before storing into Parquet.
    """

    REQUIRED_COLUMNS = {
        "timestamp",
        "trade_date",
        "symbol",
        "price",
        "volume",
    }

    VALID_SYMBOLS = {
        "TXF",
        "MXF",
        "TWII",
    }

    VALID_SESSIONS = {
        "DAY",
        "NIGHT",
    }

    def validate_schema(
        self,
        df: pl.DataFrame,
    ) -> ValidationResult:

        errors: list[str] = []
        warnings: list[str] = []

        columns = set(df.columns)

        missing_columns = self.REQUIRED_COLUMNS - columns

        if missing_columns:
            errors.append(
                f"Missing required columns: "
                f"{sorted(missing_columns)}"
            )

        if "timestamp" in df.columns:
            if df["timestamp"].dtype not in (
                pl.Datetime,
                pl.Date,
            ):
                errors.append(
                    "Column 'timestamp' must be "
                    "Datetime or Date."
                )

        if "trade_date" in df.columns:
            if df["trade_date"].dtype != pl.Date:
                errors.append(
                    "Column 'trade_date' must be Date."
                )

        if "symbol" in df.columns:
            invalid_symbols = (
                df
                .filter(
                    ~pl.col("symbol").is_in(
                        list(self.VALID_SYMBOLS)
                    )
                )
                .select("symbol")
                .unique()
                .to_series()
                .to_list()
            )

            if invalid_symbols:
                errors.append(
                    f"Invalid symbols: {invalid_symbols}"
                )

        if "session" in df.columns:
            invalid_sessions = (
                df
                .filter(
                    pl.col("session").is_not_null()
                    & ~pl.col("session").is_in(
                        list(self.VALID_SESSIONS)
                    )
                )
                .select("session")
                .unique()
                .to_series()
                .to_list()
            )

            if invalid_sessions:
                errors.append(
                    f"Invalid sessions: {invalid_sessions}"
                )

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def validate_values(
        self,
        df: pl.DataFrame,
    ) -> ValidationResult:

        errors: list[str] = []
        warnings: list[str] = []

        if df.is_empty():
            warnings.append("DataFrame is empty.")
            return ValidationResult(
                valid=True,
                errors=errors,
                warnings=warnings,
            )

        # -------------------------
        # Null checks
        # -------------------------

        for column in self.REQUIRED_COLUMNS:
            if column not in df.columns:
                continue

            null_count = df[column].null_count()

            if null_count > 0:
                errors.append(
                    f"Column '{column}' contains "
                    f"{null_count} null values."
                )

        # -------------------------
        # Price validation
        # -------------------------

        if "price" in df.columns:
            invalid_price = df.filter(
                pl.col("price") <= 0
            ).height

            if invalid_price > 0:
                errors.append(
                    f"Found {invalid_price} rows "
                    f"with price <= 0."
                )

        # -------------------------
        # Volume validation
        # -------------------------

        if "volume" in df.columns:
            invalid_volume = df.filter(
                pl.col("volume") < 0
            ).height

            if invalid_volume > 0:
                errors.append(
                    f"Found {invalid_volume} rows "
                    f"with volume < 0."
                )

        # -------------------------
        # Timestamp ordering
        # -------------------------

        if "timestamp" in df.columns:
            sorted_df = df.sort("timestamp")

            if not df.equals(sorted_df):
                warnings.append(
                    "Timestamp data is not sorted."
                )

        # -------------------------
        # Duplicate timestamp
        # -------------------------

        duplicate_columns = [
            column
            for column in [
                "timestamp",
                "symbol",
                "contract",
            ]
            if column in df.columns
        ]

        if duplicate_columns:
            duplicate_count = (
                df
                .group_by(duplicate_columns)
                .len()
                .filter(pl.col("len") > 1)
                .height
            )

            if duplicate_count > 0:
                warnings.append(
                    f"Found {duplicate_count} "
                    f"duplicate key groups."
                )

        # -------------------------
        # OHLC validation
        # -------------------------

        ohlc_columns = {
            "open",
            "high",
            "low",
            "close",
        }

        if ohlc_columns.issubset(df.columns):

            invalid_ohlc = df.filter(
                (pl.col("high") < pl.col("open"))
                | (pl.col("high") < pl.col("close"))
                | (pl.col("high") < pl.col("low"))
                | (pl.col("low") > pl.col("open"))
                | (pl.col("low") > pl.col("close"))
                | (pl.col("low") > pl.col("high"))
            ).height

            if invalid_ohlc > 0:
                errors.append(
                    f"Found {invalid_ohlc} rows "
                    f"with invalid OHLC relationship."
                )

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def validate(
        self,
        df: pl.DataFrame,
    ) -> ValidationResult:

        schema_result = self.validate_schema(df)

        if not schema_result.valid:
            return schema_result

        value_result = self.validate_values(df)

        return ValidationResult(
            valid=value_result.valid,
            errors=(
                schema_result.errors
                + value_result.errors
            ),
            warnings=(
                schema_result.warnings
                + value_result.warnings
            ),
        )