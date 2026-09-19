from pathlib import Path

import polars as pl


SOURCE_DIR = Path("data/raw/github_repo")
OUTPUT_DIR = Path("data/parquet/bar/1m")


PRODUCT_MAP = {
    "TXFR1": "TX",
    "MXFR1": "MTX",
    "TMFR1": "TMF",
}


SOURCE_FILES = [
    "data_TXFR1_2001.sql",
    "data_TXFR1_2026.sql",
    "data_MXFR1_2026.sql",
    "data_TMFR1_2026.sql",
]


def extract_rows(sql_path: Path) -> list[list[str]]:
    rows = []

    in_copy = False

    with sql_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\r\n")

            if line.startswith("COPY futures_1min"):
                in_copy = True
                continue

            if in_copy and line == r"\.":
                break

            if not in_copy:
                continue

            if not line:
                continue

            fields = line.split("\t")

            if len(fields) != 9:
                raise ValueError(
                    f"Invalid row in {sql_path.name}: "
                    f"expected 9 fields, got {len(fields)}"
                )

            rows.append(fields)

    return rows


def parse_sql_file(sql_path: Path) -> pl.DataFrame:
    rows = extract_rows(sql_path)

    if not rows:
        raise ValueError(f"No data found: {sql_path}")

    df = pl.DataFrame(
        rows,
        schema=[
            "datetime",
            "product_id",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "trading_date",
            "is_synthetic",
        ],
        orient="row",
    )

    df = df.with_columns(
        [
            pl.col("datetime")
            .str.strptime(
                pl.Datetime,
                format="%Y-%m-%d %H:%M:%S",
                strict=True,
            )
            .alias("timestamp"),

            pl.col("trading_date")
            .str.strptime(
                pl.Date,
                format="%Y-%m-%d",
                strict=True,
            ),

            pl.col("open").cast(pl.Float64),
            pl.col("high").cast(pl.Float64),
            pl.col("low").cast(pl.Float64),
            pl.col("close").cast(pl.Float64),
            pl.col("volume").cast(pl.Int64),
            (
                pl.when(pl.col("is_synthetic").str.to_lowercase() == "t")
                .then(pl.lit(True))
                .otherwise(pl.lit(False))
                .alias("is_synthetic")
             ),
        ]
    )

    df = df.with_columns(
        pl.col("product_id")
        .replace(PRODUCT_MAP)
        .alias("symbol")
    )

    unknown = df.filter(pl.col("symbol") == pl.col("product_id"))

    if unknown.height > 0:
        raise ValueError(
            f"Unknown product_id found in {sql_path.name}"
        )

    df = df.with_columns(
        [
            pl.lit("1m").alias("timeframe"),

            pl.col("product_id").alias("contract"),

            pl.when(
                pl.col("timestamp").dt.hour() >= 8
            )
            .then(pl.lit("DAY"))
            .otherwise(pl.lit("NIGHT"))
            .alias("session"),

            pl.lit("github_validation").alias("source"),
        ]
    )

    return df.select(
        [
            "timestamp",
            "trading_date",
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
    ).rename(
        {
            "trading_date": "trade_date",
        }
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for filename in SOURCE_FILES:
        sql_path = SOURCE_DIR / filename

        if not sql_path.exists():
            raise FileNotFoundError(sql_path)

        print(f"Converting: {filename}")

        df = parse_sql_file(sql_path)

        print(f"  rows: {df.height}")

        # 依日期分割，符合目前 ParquetStore 的設計
        grouped = df.with_columns(
            [
                pl.col("timestamp").dt.year().alias("_year"),
                pl.col("timestamp").dt.month().alias("_month"),
                pl.col("timestamp").dt.day().alias("_day"),
            ]
        ).partition_by(
            ["symbol", "_year", "_month", "_day"],
            as_dict=True,
        )

        for keys, part in grouped.items():
            symbol, year, month, day = keys

            path = (
                OUTPUT_DIR
                / symbol
                / f"year={year}"
                / f"month={month:02d}"
            )

            path.mkdir(parents=True, exist_ok=True)

            file_path = path / (
                f"{symbol}_{year}{month:02d}{day:02d}.parquet"
            )

            part = part.drop(
                ["_year", "_month", "_day"]
            ).sort("timestamp")

            part.write_parquet(
                file_path,
                compression="zstd",
            )

        print(f"  written: {filename}")


if __name__ == "__main__":
    main()