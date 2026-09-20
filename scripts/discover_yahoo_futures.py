import yfinance as yf

print("=" * 80)
print("Yahoo Finance Futures Lookup")
print("=" * 80)

queries = [
    "Taiwan",
    "Taiwan Index",
    "Taiwan Weighted",
    "TAIEX",
    "TXF",
    "台灣加權",
]

for query in queries:
    print()
    print("-" * 80)
    print(f"QUERY: {query}")
    print("-" * 80)

    try:
        lookup = yf.Lookup(query, timeout=30, raise_errors=False)
        df = lookup.get_future(count=100)

        print(f"Rows: {len(df)}")

        if df is None or df.empty:
            print("No futures found.")
            continue

        print("Columns:")
        print(list(df.columns))

        print()
        print(df.to_string(index=False))

    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}")
