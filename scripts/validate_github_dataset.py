from __future__ import annotations

import duckdb


DATABASE_PATH = "database/validation_github.duckdb"


def section(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def main() -> None:
    conn = duckdb.connect(DATABASE_PATH, read_only=True)

    try:
        # ============================================================
        # 1. BASIC ROW COUNT
        # ============================================================
        section("1. BASIC ROW COUNT")

        rows = conn.execute(
            """
            SELECT
                product_id,
                COUNT(*) AS row_count
            FROM github_futures_1m
            GROUP BY product_id
            ORDER BY product_id
            """
        ).fetchall()

        for row in rows:
            print(f"{row[0]}: {row[1]:,}")

        # ============================================================
        # 2. DUPLICATE DATETIME
        # ============================================================
        section("2. DUPLICATE DATETIME")

        duplicates = conn.execute(
            """
            SELECT
                product_id,
                datetime,
                COUNT(*) AS cnt
            FROM github_futures_1m
            GROUP BY product_id, datetime
            HAVING COUNT(*) > 1
            ORDER BY product_id, datetime
            LIMIT 20
            """
        ).fetchall()

        if not duplicates:
            print("OK - no duplicate (product_id, datetime)")
        else:
            print("FOUND DUPLICATES:")
            for row in duplicates:
                print(row)

        # ============================================================
        # 3. OHLC VALIDATION
        # ============================================================
        section("3. OHLC VALIDATION")

        invalid_ohlc = conn.execute(
            """
            SELECT
                product_id,
                datetime,
                open,
                high,
                low,
                close
            FROM github_futures_1m
            WHERE
                high < low
                OR high < open
                OR high < close
                OR low > open
                OR low > close
            LIMIT 20
            """
        ).fetchall()

        if not invalid_ohlc:
            print("OK - no invalid OHLC rows")
        else:
            print("FOUND INVALID OHLC:")
            for row in invalid_ohlc:
                print(row)

        # ============================================================
        # 4. NEGATIVE VOLUME
        # ============================================================
        section("4. NEGATIVE VOLUME")

        negative_volume = conn.execute(
            """
            SELECT
                product_id,
                datetime,
                volume
            FROM github_futures_1m
            WHERE volume < 0
            LIMIT 20
            """
        ).fetchall()

        if not negative_volume:
            print("OK - no negative volume")
        else:
            print("FOUND NEGATIVE VOLUME:")
            for row in negative_volume:
                print(row)

        # ============================================================
        # 5. NULL OHLC / VOLUME
        # ============================================================
        section("5. NULL OHLC / VOLUME")

        null_rows = conn.execute(
            """
            SELECT
                product_id,
                COUNT(*) AS null_count
            FROM github_futures_1m
            WHERE
                open IS NULL
                OR high IS NULL
                OR low IS NULL
                OR close IS NULL
                OR volume IS NULL
            GROUP BY product_id
            ORDER BY product_id
            """
        ).fetchall()

        if not null_rows:
            print("OK - no NULL OHLC / volume")
        else:
            print("FOUND NULL VALUES:")
            for row in null_rows:
                print(row)

        # ============================================================
        # 6. SYNTHETIC DATA
        # ============================================================
        section("6. SYNTHETIC DATA")

        synthetic = conn.execute(
            """
            SELECT
                product_id,
                is_synthetic,
                COUNT(*) AS row_count
            FROM github_futures_1m
            GROUP BY product_id, is_synthetic
            ORDER BY product_id, is_synthetic
            """
        ).fetchall()

        for row in synthetic:
            print(
                f"{row[0]} | "
                f"is_synthetic={row[1]} | "
                f"{row[2]:,} rows"
            )

        # ============================================================
        # 7. TRADING DATE RANGE
        # ============================================================
        section("7. TRADING DATE RANGE")

        dates = conn.execute(
            """
            SELECT
                product_id,
                MIN(trading_date),
                MAX(trading_date),
                COUNT(DISTINCT trading_date)
            FROM github_futures_1m
            GROUP BY product_id
            ORDER BY product_id
            """
        ).fetchall()

        for row in dates:
            print(
                f"{row[0]} | "
                f"{row[1]} -> {row[2]} | "
                f"{row[3]:,} trading dates"
            )

        # ============================================================
        # 8. DATETIME MIN/MAX
        # ============================================================
        section("8. DATETIME RANGE")

        datetime_range = conn.execute(
            """
            SELECT
                product_id,
                MIN(datetime),
                MAX(datetime)
            FROM github_futures_1m
            GROUP BY product_id
            ORDER BY product_id
            """
        ).fetchall()

        for row in datetime_range:
            print(
                f"{row[0]} | "
                f"{row[1]} -> {row[2]}"
            )

        # ============================================================
        # 9. TRADING DATE / DATETIME MISMATCH
        # ============================================================
        section("9. TRADING DATE / DATETIME MISMATCH")

        mismatch = conn.execute(
            """
            SELECT
                product_id,
                datetime,
                trading_date
            FROM github_futures_1m
            WHERE
                datetime::DATE != trading_date
                AND EXTRACT(HOUR FROM datetime) >= 6
            ORDER BY product_id, datetime
            LIMIT 30
            """
        ).fetchall()

        if not mismatch:
            print("OK - no obvious daytime mismatch")
        else:
            print("FOUND POSSIBLE MISMATCH:")
            for row in mismatch:
                print(row)

        # ============================================================
        # 10. NIGHT SESSION SAMPLE
        # ============================================================
        section("10. NIGHT SESSION SAMPLE")

        night_rows = conn.execute(
            """
            SELECT
                product_id,
                datetime,
                trading_date,
                close,
                volume
            FROM github_futures_1m
            WHERE EXTRACT(HOUR FROM datetime) < 6
            ORDER BY datetime
            LIMIT 30
            """
        ).fetchall()

        if not night_rows:
            print("No early-morning/night-session rows found.")
        else:
            for row in night_rows:
                print(row)

        # ============================================================
        # 11. MINUTES PER TRADING DATE
        # ============================================================
        section("11. MINUTES PER TRADING DATE")

        minutes = conn.execute(
            """
            SELECT
                product_id,
                trading_date,
                COUNT(*) AS rows
            FROM github_futures_1m
            GROUP BY product_id, trading_date
            ORDER BY product_id, trading_date
            LIMIT 50
            """
        ).fetchall()

        for row in minutes:
            print(
                f"{row[0]} | "
                f"{row[1]} | "
                f"{row[2]:,} rows"
            )

        # ============================================================
        # 12. ZERO VOLUME
        # ============================================================
        section("12. ZERO VOLUME")

        zero_volume = conn.execute(
            """
            SELECT
                product_id,
                COUNT(*) AS zero_volume_rows
            FROM github_futures_1m
            WHERE volume = 0
            GROUP BY product_id
            ORDER BY product_id
            """
        ).fetchall()

        for row in zero_volume:
            print(
                f"{row[0]} | "
                f"{row[1]:,} zero-volume rows"
            )

        # ============================================================
        # COMPLETE
        # ============================================================
        section("VALIDATION COMPLETE")

    finally:
        conn.close()


if __name__ == "__main__":
    main()