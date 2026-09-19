from trading_calendar.loader import (
    TradingCalendarLoader,
)

from trading_calendar.sources.taifex import (
    TAIFEXCalendarSource,
)


def main():

    source = TAIFEXCalendarSource(
        year=2026
    )

    df = source.build()

    print(
        f"Generated {df.height} calendar rows."
    )

    trading_days = (
        df
        .filter(
            df["is_trading_day"]
        )
        .height
    )

    print(
        f"Trading days: {trading_days}"
    )

    loader = TradingCalendarLoader(
        database_path="database/market.duckdb"
    )

    loader.load_dataframe(df)

    print(
        "TAIFEX 2026 calendar loaded."
    )


if __name__ == "__main__":
    main()