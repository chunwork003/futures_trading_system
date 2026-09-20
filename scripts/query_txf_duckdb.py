import duckdb


DATABASE = "database/market.duckdb"


def main():

    with duckdb.connect(
        DATABASE,
        read_only=True,
    ) as conn:

        print("=" * 70)
        print("TXF 1m DuckDB Sample Query")
        print("=" * 70)

        print()
        print("Latest 10 bars:")

        result = conn.execute(
            """
            SELECT
                timestamp,
                trade_date,
                symbol,
                contract,
                timeframe,
                open,
                high,
                low,
                close,
                volume,
                session,
                source
            FROM txf_1m
            ORDER BY timestamp DESC
            LIMIT 10
            """
        ).fetchdf()

        print(result.to_string(index=False))

        print()
        print("Dataset summary:")

        summary = conn.execute(
            """
            SELECT
                COUNT(*) AS rows,
                COUNT(DISTINCT timestamp) AS timestamps,
                MIN(timestamp) AS min_timestamp,
                MAX(timestamp) AS max_timestamp
            FROM txf_1m
            """
        ).fetchdf()

        print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
