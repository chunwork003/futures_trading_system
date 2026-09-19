from trading_calendar.sources.taifex_calendar import (
    TAIFEXCalendarSource,
)


def main():
    source = TAIFEXCalendarSource(
        raw_path="data/raw/taifex/calendar"
    )

    path = source.raw_path / "2026Calendar.pdf"

    import pymupdf

    doc = pymupdf.open(path)

    try:
        page = doc[0]

        non_trading_rects = source._extract_non_trading_rects(page)

        total = 0

        for month in range(1, 13):
            month_index = month - 1

            row_index = month_index // 3
            column_index = month_index % 3

            center_x = source.MONTH_COLUMN_CENTERS[
                column_index
            ]

            top_y = source.MONTH_ROW_TOPS[row_index]

            records = source._parse_month(
                page=page,
                year=2026,
                month=month,
                center_x=center_x,
                top_y=top_y,
                non_trading_rects=non_trading_rects,
                source_file=path.name,
            )

            print(
                f"{month:02d}: "
                f"{len(records):2d} days"
            )

            if records:
                print(
                    f"    "
                    f"{records[0].trade_date} -> "
                    f"{records[-1].trade_date}"
                )

            total += len(records)

        print()
        print(f"TOTAL: {total}")

    finally:
        doc.close()


if __name__ == "__main__":
    main()