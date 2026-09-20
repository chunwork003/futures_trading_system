from pathlib import Path

import duckdb


DATABASE_PATH = Path("database/market.duckdb")

EXPECTED_ROWS = 185_420


def main():
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB database not found: {DATABASE_PATH}"
        )

    with duckdb.connect(str(DATABASE_PATH), read_only=True) as conn:

        print("=" * 70)
        print("TXF 1m DuckDB Validation")
        print("=" * 70)

        print()
        print("1. View")
        view_exists = conn.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.views
            WHERE table_name = 'txf_1m'
            """
        ).fetchone()[0]

        print(f"txf_1m exists: {view_exists == 1}")

        if view_exists != 1:
            raise AssertionError(
                "DuckDB view txf_1m does not exist"
            )

        print()
        print("2. Row count")

        row_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM txf_1m
            """
        ).fetchone()[0]

        print(f"Rows: {row_count:,}")

        if row_count != EXPECTED_ROWS:
            raise AssertionError(
                f"Unexpected row count: {row_count:,}"
            )

        print()
        print("3. Time range")

        time_range = conn.execute(
            """
            SELECT
                MIN(timestamp),
                MAX(timestamp)
            FROM txf_1m
            """
        ).fetchone()

        print(f"Min timestamp: {time_range[0]}")
        print(f"Max timestamp: {time_range[1]}")

        if str(time_range[0]) != "2026-01-01 00:00:00":
            raise AssertionError(
                f"Unexpected minimum timestamp: {time_range[0]}"
            )

        if str(time_range[1]) != "2026-09-05 04:59:00":
            raise AssertionError(
                f"Unexpected maximum timestamp: {time_range[1]}"
            )

        print()
        print("4. Trade date range")

        trade_range = conn.execute(
            """
            SELECT
                MIN(trade_date),
                MAX(trade_date)
            FROM txf_1m
            """
        ).fetchone()

        print(f"Min trade date: {trade_range[0]}")
        print(f"Max trade date: {trade_range[1]}")

        if str(trade_range[0]) != "2026-01-02":
            raise AssertionError(
                f"Unexpected minimum trade date: {trade_range[0]}"
            )

        if str(trade_range[1]) != "2026-09-07":
            raise AssertionError(
                f"Unexpected maximum trade date: {trade_range[1]}"
            )

        print()
        print("5. Symbol")

        symbols = conn.execute(
            """
            SELECT symbol, COUNT(*) AS rows
            FROM txf_1m
            GROUP BY symbol
            ORDER BY symbol
            """
        ).fetchall()

        for row in symbols:
            print(row)

        if symbols != [("TXF", EXPECTED_ROWS)]:
            raise AssertionError(
                f"Unexpected symbols: {symbols}"
            )

        print()
        print("6. Source")

        sources = conn.execute(
            """
            SELECT source, COUNT(*) AS rows
            FROM txf_1m
            GROUP BY source
            ORDER BY source
            """
        ).fetchall()

        for row in sources:
            print(row)

        if sources != [("github", EXPECTED_ROWS)]:
            raise AssertionError(
                f"Unexpected sources: {sources}"
            )

        print()
        print("7. Duplicate keys")

        duplicates = conn.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT
                    timestamp,
                    symbol,
                    contract,
                    timeframe
                FROM txf_1m
                GROUP BY
                    timestamp,
                    symbol,
                    contract,
                    timeframe
                HAVING COUNT(*) > 1
            )
            """
        ).fetchone()[0]

        print(f"Duplicate keys: {duplicates}")

        if duplicates != 0:
            raise AssertionError(
                "Duplicate canonical bars detected"
            )

        print()
        print("8. NULL required fields")

        nulls = conn.execute(
            """
            SELECT
                COUNT(*) FILTER (WHERE timestamp IS NULL),
                COUNT(*) FILTER (WHERE trade_date IS NULL),
                COUNT(*) FILTER (WHERE symbol IS NULL),
                COUNT(*) FILTER (WHERE contract IS NULL),
                COUNT(*) FILTER (WHERE timeframe IS NULL),
                COUNT(*) FILTER (WHERE open IS NULL),
                COUNT(*) FILTER (WHERE high IS NULL),
                COUNT(*) FILTER (WHERE low IS NULL),
                COUNT(*) FILTER (WHERE close IS NULL),
                COUNT(*) FILTER (WHERE volume IS NULL),
                COUNT(*) FILTER (WHERE source IS NULL)
            FROM txf_1m
            """
        ).fetchone()

        print(f"NULL counts: {nulls}")

        if any(value != 0 for value in nulls):
            raise AssertionError(
                "NULL values found in required fields"
            )

        print()
        print("9. Invalid OHLC")

        invalid_ohlc = conn.execute(
            """
            SELECT COUNT(*)
            FROM txf_1m
            WHERE
                high < GREATEST(open, high, low, close)
                OR low > LEAST(open, high, low, close)
            """
        ).fetchone()[0]

        print(f"Invalid OHLC: {invalid_ohlc}")

        if invalid_ohlc != 0:
            raise AssertionError(
                "Invalid OHLC bars detected"
            )

        print()
        print("10. Negative volume")

        negative_volume = conn.execute(
            """
            SELECT COUNT(*)
            FROM txf_1m
            WHERE volume < 0
            """
        ).fetchone()[0]

        print(f"Negative volume: {negative_volume}")

        if negative_volume != 0:
            raise AssertionError(
                "Negative volume detected"
            )

        print()
        print("11. Session distribution")

        sessions = conn.execute(
            """
            SELECT
                session,
                COUNT(*) AS rows
            FROM txf_1m
            GROUP BY session
            ORDER BY session
            """
        ).fetchall()

        for row in sessions:
            print(row)

        print()
        print("12. Contract distribution")

        contracts = conn.execute(
            """
            SELECT
                contract,
                COUNT(*) AS rows
            FROM txf_1m
            GROUP BY contract
            ORDER BY contract
            """
        ).fetchall()

        for row in contracts:
            print(row)

        print()
        print("=" * 70)
        print("DuckDB Validation PASSED")
        print("=" * 70)


if __name__ == "__main__":
    main()
