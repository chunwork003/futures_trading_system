from pathlib import Path
import duckdb


DATABASE_PATH = Path("database/validation_github.duckdb")


def main() -> None:
    conn = duckdb.connect(str(DATABASE_PATH))

    try:
        print("=" * 70)
        print("GAP NEIGHBOR ANALYSIS")
        print("=" * 70)

        rows = conn.execute(
            """
            WITH ordered AS (
                SELECT
                    product_id,
                    trading_date,
                    datetime,
                    open,
                    high,
                    low,
                    close,
                    volume,
                    LAG(datetime) OVER (
                        PARTITION BY product_id, trading_date
                        ORDER BY datetime
                    ) AS prev_datetime,
                    LAG(close) OVER (
                        PARTITION BY product_id, trading_date
                        ORDER BY datetime
                    ) AS prev_close,
                    LAG(volume) OVER (
                        PARTITION BY product_id, trading_date
                        ORDER BY datetime
                    ) AS prev_volume
                FROM github_futures_1m
            )
            SELECT
                product_id,
                trading_date,
                prev_datetime,
                prev_close,
                prev_volume,
                datetime,
                open,
                high,
                low,
                close,
                volume,
                DATE_DIFF(
                    'minute',
                    prev_datetime,
                    datetime
                ) AS gap_minutes
            FROM ordered
            WHERE DATE_DIFF(
                    'minute',
                    prev_datetime,
                    datetime
                  ) > 1
              AND EXTRACT(HOUR FROM datetime) < 6
              AND EXTRACT(HOUR FROM prev_datetime) < 6
            ORDER BY
                gap_minutes DESC,
                product_id,
                trading_date
            LIMIT 100
            """
        ).fetchall()

        for row in rows:
            print(row)

    finally:
        conn.close()


if __name__ == "__main__":
    main()