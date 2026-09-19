from pathlib import Path

import duckdb


DATABASE_PATH = Path(
    "database/market.duckdb"
)

SCHEMA_PATH = Path(
    "database/schema"
)


def initialize_database() -> None:

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = duckdb.connect(
        str(DATABASE_PATH)
    )

    schema_files = [
        "01_instrument.sql",
        "02_contract.sql",
        "03_calendar.sql",
        "03_calendar_exception.sql",
        "04_continuous.sql",
        "05_backtest.sql",
    ]

    try:
        for filename in schema_files:
            path = SCHEMA_PATH / filename

            if not path.exists():
                raise FileNotFoundError(
                    f"Schema file not found: {path}"
                )

            sql = path.read_text(
                encoding="utf-8"
            )

            conn.execute(sql)

    finally:
        conn.close()


if __name__ == "__main__":

    initialize_database()

    print("DuckDB initialized.")