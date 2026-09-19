import duckdb

DATABASE_PATH = "database/market.duckdb"

conn = duckdb.connect(DATABASE_PATH)

print("=== Calendar Summary ===")

print(
    conn.execute("""
        SELECT
            MIN(trade_date) AS min_date,
            MAX(trade_date) AS max_date,
            COUNT(*) AS total_rows,
            COUNT(DISTINCT trade_date) AS unique_dates,
            SUM(CASE WHEN is_trading_day THEN 1 ELSE 0 END) AS trading_days,
            SUM(CASE WHEN NOT is_trading_day THEN 1 ELSE 0 END) AS non_trading_days
        FROM trading_calendar
    """).fetchdf()
)

print("\n=== Duplicate Dates ===")

print(
    conn.execute("""
        SELECT
            trade_date,
            COUNT(*) AS cnt
        FROM trading_calendar
        GROUP BY trade_date
        HAVING COUNT(*) > 1
        ORDER BY trade_date
    """).fetchdf()
)

print("\n=== Session Integrity Errors ===")

print(
    conn.execute("""
        SELECT
            trade_date,
            is_trading_day,
            day_session,
            night_session,
            day_open,
            day_close,
            night_open,
            night_close
        FROM trading_calendar
        WHERE
            (
                is_trading_day = TRUE
                AND (
                    day_session = FALSE
                    OR night_session = FALSE
                    OR day_open IS NULL
                    OR day_close IS NULL
                    OR night_open IS NULL
                    OR night_close IS NULL
                )
            )
            OR
            (
                is_trading_day = FALSE
                AND (
                    day_session = TRUE
                    OR night_session = TRUE
                )
            )
        ORDER BY trade_date
    """).fetchdf()
)

print("\n=== Special Dates ===")

special_dates = [
    "2026-07-10",
    "2026-09-16",
    "2026-09-25",
    "2026-09-28",
]

for date in special_dates:
    row = conn.execute(
        """
        SELECT
            trade_date,
            is_trading_day,
            day_session,
            night_session,
            notes
        FROM trading_calendar
        WHERE trade_date = ?
        """,
        [date],
    ).fetchone()

    print(row)

conn.close()
