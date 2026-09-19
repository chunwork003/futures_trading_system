from __future__ import annotations

from pathlib import Path
import duckdb


BASE_DIR = Path(__file__).resolve().parents[1]

SOURCE_DIR = BASE_DIR / "data" / "raw" / "github_repo"
DATABASE_PATH = BASE_DIR / "database" / "validation_github.duckdb"
TEMP_DIR = BASE_DIR / "data" / "raw" / "_validation_tmp"


TEST_FILES = [
    "data_TXFR1_2001.sql",
    "data_TXFR1_2026.sql",
    "data_MXFR1_2026.sql",
    "data_TMFR1_2026.sql",
]


def extract_copy_data(path: Path) -> Path:

    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    temp_path = TEMP_DIR / f"{path.stem}.tsv"

    print(f"Extracting: {path.name}")

    in_copy = False
    row_count = 0

    with path.open("r", encoding="utf-8") as source, \
         temp_path.open("w", encoding="utf-8", newline="") as target:

        for raw_line in source:

            line = raw_line.rstrip("\r\n")

            if not in_copy:

                if line.startswith("COPY futures_1min"):
                    in_copy = True

                continue

            if line == r"\.":
                break

            if not line:
                continue

            target.write(line + "\n")
            row_count += 1

    if row_count == 0:
        raise ValueError(
            f"No data rows found in {path.name}"
        )

    print(f"  rows extracted: {row_count:,}")

    return temp_path


def import_file(
    conn: duckdb.DuckDBPyConnection,
    path: Path,
) -> int:

    temp_path = extract_copy_data(path)

    print(f"Loading into DuckDB: {path.name}")

    conn.execute(
        """
        INSERT INTO github_futures_1m (
            datetime,
            product_id,
            open,
            high,
            low,
            close,
            volume,
            trading_date,
            is_synthetic,
            source_file
        )
        SELECT
            CAST(column0 AS TIMESTAMP),
            column1,
            CAST(column2 AS DOUBLE),
            CAST(column3 AS DOUBLE),
            CAST(column4 AS DOUBLE),
            CAST(column5 AS DOUBLE),
            CAST(column6 AS BIGINT),
            CAST(column7 AS DATE),
            CAST(column8 AS BOOLEAN),
            ?
        FROM read_csv(
            ?,
            delim = '\t',
            header = false,
            columns = {
                'column0': 'VARCHAR',
                'column1': 'VARCHAR',
                'column2': 'VARCHAR',
                'column3': 'VARCHAR',
                'column4': 'VARCHAR',
                'column5': 'VARCHAR',
                'column6': 'VARCHAR',
                'column7': 'VARCHAR',
                'column8': 'VARCHAR'
            }
        )
        """,
        [path.name, str(temp_path)],
    )

    temp_path.unlink(missing_ok=True)

    print(f"  loaded: {path.name}")

    return 1


def main() -> None:

    files = [
        SOURCE_DIR / filename
        for filename in TEST_FILES
    ]

    for path in files:

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {path}"
            )

    print(f"Source directory: {SOURCE_DIR}")
    print(f"SQL files found: {len(files)}")
    print()

    conn = duckdb.connect(str(DATABASE_PATH))

    try:

        for path in files:
            import_file(conn, path)

        print()
        print("=" * 60)

        result = conn.execute(
            """
            SELECT
                product_id,
                COUNT(*) AS rows,
                MIN(datetime) AS min_datetime,
                MAX(datetime) AS max_datetime,
                MIN(trading_date) AS min_trade_date,
                MAX(trading_date) AS max_trade_date
            FROM github_futures_1m
            GROUP BY product_id
            ORDER BY product_id
            """
        ).fetchall()

        print("Database summary:")

        for row in result:

            print(
                f"{row[0]}: "
                f"{row[1]:,} rows | "
                f"{row[2]} -> {row[3]} | "
                f"trade_date "
                f"{row[4]} -> {row[5]}"
            )

    finally:
        conn.close()


if __name__ == "__main__":
    main()
