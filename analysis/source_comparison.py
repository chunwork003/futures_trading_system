from dataclasses import dataclass
from typing import Optional

import polars as pl


KEY_COLUMNS = [
    "timestamp",
    "symbol",
    "contract",
    "timeframe",
]

PRICE_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
]

COMPARE_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
]


@dataclass(frozen=True)
class SourceComparisonReport:
    source_a: str
    source_b: str

    rows_a: int
    rows_b: int

    matched_rows: int
    missing_in_a: int
    missing_in_b: int

    price_mismatch_rows: int
    volume_mismatch_rows: int

    max_open_diff: Optional[float]
    max_high_diff: Optional[float]
    max_low_diff: Optional[float]
    max_close_diff: Optional[float]
    max_volume_diff: Optional[int]


class SourceComparator:

    def compare(
        self,
        df_a: pl.DataFrame,
        df_b: pl.DataFrame,
        source_a: str,
        source_b: str,
    ) -> SourceComparisonReport:

        required = set(
            KEY_COLUMNS + COMPARE_COLUMNS
        )

        missing_a = required - set(df_a.columns)
        missing_b = required - set(df_b.columns)

        if missing_a:
            raise ValueError(
                f"Source A missing columns: {missing_a}"
            )

        if missing_b:
            raise ValueError(
                f"Source B missing columns: {missing_b}"
            )

        a = df_a.select(
            KEY_COLUMNS + COMPARE_COLUMNS
        )

        b = df_b.select(
            KEY_COLUMNS + COMPARE_COLUMNS
        )

        rows_a = a.height
        rows_b = b.height

        keys_a = a.select(KEY_COLUMNS).unique()
        keys_b = b.select(KEY_COLUMNS).unique()

        only_a = (
            keys_a.join(
                keys_b,
                on=KEY_COLUMNS,
                how="anti",
            )
        )

        only_b = (
            keys_b.join(
                keys_a,
                on=KEY_COLUMNS,
                how="anti",
            )
        )

        matched = (
            a.join(
                b,
                on=KEY_COLUMNS,
                how="inner",
                suffix="_b",
            )
        )

        price_mismatch = matched.filter(
            (pl.col("open") != pl.col("open_b"))
            | (pl.col("high") != pl.col("high_b"))
            | (pl.col("low") != pl.col("low_b"))
            | (pl.col("close") != pl.col("close_b"))
        )

        volume_mismatch = matched.filter(
            pl.col("volume") != pl.col("volume_b")
        )

        diffs = matched.with_columns([
            (pl.col("open") - pl.col("open_b"))
            .abs()
            .alias("open_diff"),

            (pl.col("high") - pl.col("high_b"))
            .abs()
            .alias("high_diff"),

            (pl.col("low") - pl.col("low_b"))
            .abs()
            .alias("low_diff"),

            (pl.col("close") - pl.col("close_b"))
            .abs()
            .alias("close_diff"),

            (pl.col("volume") - pl.col("volume_b"))
            .abs()
            .alias("volume_diff"),
        ])

        max_values = diffs.select([
            pl.col("open_diff").max(),
            pl.col("high_diff").max(),
            pl.col("low_diff").max(),
            pl.col("close_diff").max(),
            pl.col("volume_diff").max(),
        ]).row(0)

        return SourceComparisonReport(
            source_a=source_a,
            source_b=source_b,

            rows_a=rows_a,
            rows_b=rows_b,

            matched_rows=matched.height,
            missing_in_a=only_b.height,
            missing_in_b=only_a.height,

            price_mismatch_rows=price_mismatch.height,
            volume_mismatch_rows=volume_mismatch.height,

            max_open_diff=max_values[0],
            max_high_diff=max_values[1],
            max_low_diff=max_values[2],
            max_close_diff=max_values[3],
            max_volume_diff=(
                int(max_values[4])
                if max_values[4] is not None
                else None
            ),
        )
