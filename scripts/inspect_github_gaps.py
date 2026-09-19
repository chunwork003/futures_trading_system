from pathlib import Path
import duckdb


DATABASE_PATH = Path("database/validation_github.duckdb")


def main() -> None:
    conn = duckdb.connect(str(DATABASE_PATH))

    try:
        print("=" * 70)
        print("1. BASIC SUMMARY")
        print("=" * 70)

        rows = conn.execute(
            """
            SELECT
                product_id,
                COUNT(*) AS total_rows,
                SUM(CASE WHEN volume = 0 THEN 1 ELSE 0 END) AS zero_volume_rows,
                MIN(datetime) AS min_datetime,
                MAX(datetime) AS max_datetime
            FROM github_futures_1m
            GROUP BY product_id
            ORDER BY product_id
            """
        ).fetchall()

        for row in rows:
            print(row)

        print()
        print("=" * 70)
        print("2. SMALL GAPS INSIDE EARLY-MORNING NIGHT SESSION")
        print("=" * 70)

        rows = conn.execute(
            """
            WITH ordered AS (
                SELECT
                    product_id,
                    trading_date,
                    datetime,
                    volume,
                    LAG(datetime) OVER (
                        PARTITION BY product_id, trading_date
                        ORDER BY datetime
                    ) AS prev_datetime
                FROM github_futures_1m
            )
            SELECT
                product_id,
                trading_date,
                prev_datetime,
                datetime,
                DATE_DIFF(
                    'minute',
                    prev_datetime,
                    datetime
                ) AS gap_minutes,
                volume
            FROM ordered
            WHERE DATE_DIFF(
                    'minute',
                    prev_datetime,
                    datetime
                  ) > 1
              AND EXTRACT(HOUR FROM datetime) < 6
              AND EXTRACT(HOUR FROM prev_datetime) < 6
              AND DATE_DIFF(
                    'minute',
                    prev_datetime,
                    datetime
                  ) <= 10
            ORDER BY
                product_id,
                trading_date,
                datetime
            LIMIT 100
            """
        ).fetchall()

        if not rows:
            print("No small gaps found.")
        else:
            for row in rows:
                print(row)

        print()
        print("=" * 70)
        print("3. GAP COUNT")
        print("=" * 70)

        rows = conn.execute(
            """
            WITH ordered AS (
                SELECT
                    product_id,
                    trading_date,
                    datetime,
                    LAG(datetime) OVER (
                        PARTITION BY product_id, trading_date
                        ORDER BY datetime
                    ) AS prev_datetime
                FROM github_futures_1m
            )
            SELECT
                product_id,
                COUNT(*) AS gap_count,
                MAX(
                    DATE_DIFF(
                        'minute',
                        prev_datetime,
                        datetime
                    )
                ) AS max_gap_minutes
            FROM ordered
            WHERE DATE_DIFF(
                    'minute',
                    prev_datetime,
                    datetime
                  ) > 1
              AND EXTRACT(HOUR FROM datetime) < 6
              AND EXTRACT(HOUR FROM prev_datetime) < 6
            GROUP BY product_id
            ORDER BY product_id
            """
        ).fetchall()

        for row in rows:
            print(row)

    finally:
        conn.close()


if __name__ == "__main__":
    main()