from pathlib import Path
from typing import Iterator

import polars as pl


RAW_COLUMNS = [
    "datetime_raw",
    "product_id",
    "open_raw",
    "high_raw",
    "low_raw",
    "close_raw",
    "volume_raw",
    "trade_date_raw",
    "is_synthetic_raw",
]


def _parse_copy_row(line: str) -> tuple:
    line = line.rstrip("\r\n")

    values = line.split("\t")

    if len(values) != 9:
        tokens = line.split()

        if len(tokens) != 10:
            raise ValueError(
                f"Unexpected COPY row column count: {len(tokens)}"
            )

        values = [
            f"{tokens[0]} {tokens[1]}",
            *tokens[2:],
        ]

    if len(values) != 9:
        raise ValueError(
            f"Unexpected COPY row column count: {len(values)}"
        )

    return tuple(
        None if value == r"\N" else value
        for value in values
    )


def iter_txf_sql_rows(
    path: str | Path,
) -> Iterator[tuple]:
    """Stream raw rows from a PostgreSQL COPY dump."""

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(path)

    in_copy = False

    with path.open(
        "r",
        encoding="utf-8",
        buffering=1024 * 1024,
    ) as file:
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

            yield _parse_copy_row(line)


def iter_txf_sql_batches(
    path: str | Path,
    batch_size: int = 100_000,
) -> Iterator[pl.DataFrame]:
    """Yield canonical TXF DataFrames in bounded-size batches."""

    if batch_size <= 0:
        raise ValueError("batch_size must be > 0")

    rows: list[tuple] = []

    for row in iter_txf_sql_rows(path):
        rows.append(row)

        if len(rows) >= batch_size:
            yield _canonicalize_batch(rows)
            rows.clear()

    if rows:
        yield _canonicalize_batch(rows)


def _canonicalize_batch(
    rows: list[tuple],
) -> pl.DataFrame:
    df = pl.DataFrame(
        rows,
        schema=RAW_COLUMNS,
        orient="row",
    )

    return (
        df.with_columns(
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
        .with_columns(
            [
                pl.lit("TXF").alias("symbol"),
                pl.col("product_id").alias("contract"),
                pl.lit("1m").alias("timeframe"),
                pl.lit(None, dtype=pl.String).alias("session"),
                pl.lit("github").alias("source"),
            ]
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
        .sort("timestamp")
    )
