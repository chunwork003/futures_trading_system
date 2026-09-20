from pathlib import Path

import polars as pl


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


def _parse_copy_row(line: str) -> tuple:
    """Parse one PostgreSQL COPY row.

    Supports:
    1. Standard TAB-delimited PostgreSQL COPY rows.
    2. Whitespace-separated fixtures where datetime contains a space.
    """

    line = line.rstrip("\r\n")

    # Standard PostgreSQL COPY format.
    values = line.split("\t")

    if len(values) == 9:
        parsed = values
    else:
        # Fallback for whitespace-separated data.
        # Datetime consists of two tokens:
        # YYYY-MM-DD HH:MM:SS
        tokens = line.split()

        if len(tokens) != 10:
            raise ValueError(
                f"Unexpected COPY row column count: {len(tokens)}"
            )

        parsed = [
            f"{tokens[0]} {tokens[1]}",
            *tokens[2:],
        ]

    if len(parsed) != 9:
        raise ValueError(
            f"Unexpected COPY row column count: {len(parsed)}"
        )

    return tuple(
        None if value == r"\N" else value
        for value in parsed
    )


def parse_txf_sql(
    path: str | Path,
    source: str = "github",
) -> pl.DataFrame:
    """Parse a TXFR1 PostgreSQL COPY dump into canonical 1-minute bars."""

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(path)

    rows: list[tuple] = []
    in_copy = False

    with path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.rstrip("\r\n")

            if line.startswith("COPY futures_1min"):
                in_copy = True
                continue

            if in_copy and line == r"\.":
                in_copy = False
                continue

            if not in_copy:
                continue

            if not line.strip():
                continue

            rows.append(_parse_copy_row(line))

    if not rows:
        return pl.DataFrame(
            schema={
                "timestamp": pl.Datetime,
                "trade_date": pl.Date,
                "symbol": pl.String,
                "contract": pl.String,
                "timeframe": pl.String,
                "open": pl.Float64,
                "high": pl.Float64,
                "low": pl.Float64,
                "close": pl.Float64,
                "volume": pl.Int64,
                "session": pl.String,
                "source": pl.String,
            }
        )

    df = pl.DataFrame(
        rows,
        schema=[
            "datetime_raw",
            "product_id",
            "open_raw",
            "high_raw",
            "low_raw",
            "close_raw",
            "volume_raw",
            "trade_date_raw",
            "is_synthetic_raw",
        ],
        orient="row",
    )

    df = df.with_columns(
        [
            pl.col("datetime_raw")
            .str.to_datetime(
                format="%Y-%m-%d %H:%M:%S",
                strict=True,
            )
            .alias("timestamp"),

            pl.col("trade_date_raw")
            .str.to_date(
                format="%Y-%m-%d",
                strict=True,
            )
            .alias("trade_date"),

            pl.col("open_raw")
            .cast(pl.Float64)
            .alias("open"),

            pl.col("high_raw")
            .cast(pl.Float64)
            .alias("high"),

            pl.col("low_raw")
            .cast(pl.Float64)
            .alias("low"),

            pl.col("close_raw")
            .cast(pl.Float64)
            .alias("close"),

            pl.col("volume_raw")
            .cast(pl.Int64)
            .alias("volume"),
        ]
    )

    return (
        df.with_columns(
            [
                pl.lit("TXF").alias("symbol"),
                pl.col("product_id").alias("contract"),
                pl.lit("1m").alias("timeframe"),
                pl.lit(None, dtype=pl.String).alias("session"),
                pl.lit(source).alias("source"),
            ]
        )
        .select(CANONICAL_COLUMNS)
        .sort("timestamp")
    )


def filter_date_range(
    df: pl.DataFrame,
    start_date,
    end_date,
) -> pl.DataFrame:
    """Filter canonical bars by inclusive trade date."""

    return df.filter(
        pl.col("trade_date").is_between(
            start_date,
            end_date,
            closed="both",
        )
    )


def validate_canonical_bars(df: pl.DataFrame) -> None:
    """Validate canonical OHLCV bars."""

    required = set(CANONICAL_COLUMNS)

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing canonical columns: {sorted(missing)}"
        )

    if df.select(
        pl.any_horizontal(
            pl.col(CANONICAL_COLUMNS).is_null()
        )
    ).item():
        raise ValueError("Canonical bars contain null values.")

    invalid_ohlc = df.filter(
        (pl.col("high") < pl.max_horizontal(
            "open", "close", "low"
        ))
        |
        (pl.col("low") > pl.min_horizontal(
            "open", "close", "high"
        ))
    )

    if invalid_ohlc.height > 0:
        raise ValueError(
            f"Invalid OHLC rows: {invalid_ohlc.height}"
        )

    invalid_volume = df.filter(
        pl.col("volume") < 0
    )

    if invalid_volume.height > 0:
        raise ValueError(
            f"Invalid volume rows: {invalid_volume.height}"
        )
