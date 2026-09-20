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


class CanonicalParquetWriter:

    def __init__(
        self,
        base_path: str = "data/parquet",
        staging_path: str = "data/staging/parquet",
    ):
        self.base_path = Path(base_path)
        self.staging_path = Path(staging_path)

    def write_batch(
        self,
        df: pl.DataFrame,
        dataset: str,
        symbol: str,
        batch_id: int,
    ) -> list[Path]:

        if df.is_empty():
            return []

        written = []

        for group in df.partition_by(
            "trade_date",
            maintain_order=True,
        ):
            trade_date = group["trade_date"][0]

            year = trade_date.year
            month = trade_date.month
            day = trade_date.day

            path = (
                self.staging_path
                / dataset
                / symbol
                / f"year={year}"
                / f"month={month:02d}"
                / f"trade_date={trade_date}"
            )

            path.mkdir(
                parents=True,
                exist_ok=True,
            )

            file_path = (
                path
                / f"{symbol}_{year}{month:02d}{day:02d}"
                f".part-{batch_id:06d}.parquet"
            )

            group.write_parquet(
                file_path,
                compression="zstd",
            )

            written.append(file_path)

        return written

    def compact(
        self,
        dataset: str = "bar/1m",
        symbol: str = "TXF",
    ) -> list[Path]:

        staging_root = (
            self.staging_path
            / dataset
            / symbol
        )

        if not staging_root.exists():
            return []

        final_root = (
            self.base_path
            / dataset
            / symbol
        )

        final_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        part_files = sorted(
            staging_root.rglob("*.parquet")
        )

        groups: dict[str, list[Path]] = {}

        for file_path in part_files:
            trade_date = file_path.parent.name.replace(
                "trade_date=",
                "",
            )

            groups.setdefault(
                trade_date,
                [],
            ).append(file_path)

        final_files = []

        for trade_date_text, files in sorted(
            groups.items()
        ):

            frames = [
                pl.read_parquet(path)
                for path in files
            ]

            df = (
                pl.concat(
                    frames,
                    how="vertical",
                )
                .select(CANONICAL_COLUMNS)
                .sort("timestamp")
            )

            duplicates = (
                df.group_by(
                    [
                        "timestamp",
                        "symbol",
                        "contract",
                        "timeframe",
                    ]
                )
                .len()
                .filter(pl.col("len") > 1)
            )

            if duplicates.height > 0:
                raise ValueError(
                    f"Duplicate canonical bars found: "
                    f"{trade_date_text}"
                )

            trade_date = df["trade_date"][0]

            year = trade_date.year
            month = trade_date.month
            day = trade_date.day

            final_dir = (
                final_root
                / f"year={year}"
                / f"month={month:02d}"
            )

            final_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            final_file = (
                final_dir
                / f"{symbol}_{year}{month:02d}{day:02d}.parquet"
            )

            df.write_parquet(
                final_file,
                compression="zstd",
            )

            final_files.append(final_file)

        return final_files

    def scan(
        self,
        dataset: str,
        symbol: str,
    ) -> pl.LazyFrame:

        path = (
            self.base_path
            / dataset
            / symbol
            / "**/*.parquet"
        )

        return pl.scan_parquet(
            str(path),
            hive_partitioning=True,
        )
