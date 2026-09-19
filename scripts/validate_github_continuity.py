from __future__ import annotations

import duckdb


DATABASE_PATH = "database/validation_github.duckdb"


def main() -> None:
    conn = duckdb.connect(DATABASE_PATH, read_only=True)

    try:
        print("=" * 70)
        print("1. CONSECUTIVE MINUTE CHECK")
        print("=" * 70)

        result = conn.execute(
            """
            WITH ordered AS (
                SELECT
                    product_id,
                    datetime,
                    trading_date,
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
                date_diff(
                    'minute',
                    prev_datetime,
                    datetime
                ) AS minute_gap
            FROM ordered
            WHERE
                prev_datetime IS NOT NULL
                AND date_diff(
                    'minute',
                    prev_datetime,
                    datetime
                ) > 1
            ORDER BY
                product_id,
                trading_date,
                datetime
            LIMIT 100
            """
        ).fetchall()

        if not result:
            print("OK - no gaps greater than 1 minute")
        else:
            print("FOUND TIME GAPS:")
            for row in result:
                print(row)

        print()
        print("=" * 70)
        print("2. GAP SUMMARY")
        print("=" * 70)

        summary = conn.execute(
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
            ),
            gaps AS (
                SELECT
                    product_id,
                    trading_date,
                    date_diff(
                        'minute',
                        prev_datetime,
                        datetime
                    ) AS minute_gap
                FROM ordered
                WHERE
                    prev_datetime IS NOT NULL
                    AND date_diff(
                        'minute',
                        prev_datetime,
                        datetime
                    ) > 1
            )
            SELECT
                product_id,
                COUNT(*) AS gap_count,
                MAX(minute_gap) AS max_gap
            FROM gaps
            GROUP BY product_id
            ORDER BY product_id
            """
        ).fetchall()

        if not summary:
            print("OK - no gaps detected")
        else:
            for row in summary:
                print(
                    f"{row[0]} | "
                    f"gap_count={row[1]:,} | "
                    f"max_gap={row[2]} minutes"
                )

        print()
        print("=" * 70)
        print("3. LARGEST GAPS")
        print("=" * 70)

        largest = conn.execute(
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
                trading_date,
                prev_datetime,
                datetime,
                date_diff(
                    'minute',
                    prev_datetime,
                    datetime
                ) AS minute_gap
            FROM ordered
            WHERE
                prev_datetime IS NOT NULL
                AND date_diff(
                    'minute',
                    prev_datetime,
                    datetime
                ) > 1
            ORDER BY minute_gap DESC
            LIMIT 30
            """
        ).fetchall()

        for row in largest:
            print(row)

        print()
        print("=" * 70)
        print("CONTINUITY VALIDATION COMPLETE")
        print("=" * 70)

    finally:
        conn.close()


if __name__ == "__main__":
    main()