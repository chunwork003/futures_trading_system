from datetime import date

from ingestion.yahoo import YahooDataSource


def print_result(title: str, df) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

    print(f"Rows: {df.height}")

    if df.is_empty():
        print("No data returned.")
        return

    print(f"Columns: {df.columns}")
    print(f"Min timestamp: {df['timestamp'].min()}")
    print(f"Max timestamp: {df['timestamp'].max()}")
    print(f"Symbol: {df['symbol'].unique().to_list()}")
    print(f"Contract: {df['contract'].unique().to_list()}")
    print(f"Timeframe: {df['timeframe'].unique().to_list()}")
    print(f"Source: {df['source'].unique().to_list()}")

    print()
    print(df.head(5))


def main() -> None:
    source = YahooDataSource()

    print(f"Yahoo source: {source.source_name}")

    df = source.download(
        start_date=date(2026, 9, 17),
        end_date=date(2026, 9, 18),
        symbol="TWII",
        timeframe="1d",
    )

    print_result(
        "TWII / ^TWII / 1d / Reference Only",
        df,
    )


if __name__ == "__main__":
    main()
