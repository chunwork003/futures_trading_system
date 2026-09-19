import duckdb

conn = duckdb.connect("database/market.duckdb")

print("=== INSTRUMENTS ===")

rows = conn.execute("""
    SELECT
        instrument_id,
        symbol,
        name,
        asset_type,
        exchange,
        currency,
        multiplier,
        tick_size
    FROM instruments
    ORDER BY instrument_id
""").fetchall()

for row in rows:
    print(row)

print("\n=== CONTRACTS ===")

rows = conn.execute("""
    SELECT
        contract_id,
        instrument_id,
        contract_code,
        contract_month,
        listing_date,
        last_trade_date,
        settlement_date,
        status
    FROM contracts
    ORDER BY instrument_id, contract_id
""").fetchall()

for row in rows:
    print(row)

conn.close()
