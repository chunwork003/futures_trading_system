from pathlib import Path

import duckdb


DATABASE_PATH = Path("database/market.duckdb")
VIEW_PATH = Path("database/views/txf_1m.sql")


def main():
    if not DATABASE_PATH.parent.exists():
        DATABASE_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    if not VIEW_PATH.exists():
        raise FileNotFoundError(
            f"View SQL not found: {VIEW_PATH}"
        )

    sql = VIEW_PATH.read_text(
        encoding="utf-8"
    )

    with duckdb.connect(str(DATABASE_PATH)) as conn:
        conn.execute(sql)

        result = conn.execute(
            """
            SELECT COUNT(*)
            FROM txf_1m
            """
        ).fetchone()

    print("=" * 70)
    print("DuckDB TXF 1m Registration")
    print("=" * 70)
    print(f"Database: {DATABASE_PATH}")
    print("View:     txf_1m")
    print(f"Rows:     {result[0]:,}")
    print()
    print("DuckDB registration PASSED")


if __name__ == "__main__":
    main()
