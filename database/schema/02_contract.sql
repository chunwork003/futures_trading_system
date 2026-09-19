CREATE TABLE IF NOT EXISTS contracts (
    contract_id BIGINT PRIMARY KEY,
    instrument_id INTEGER NOT NULL,
    contract_code VARCHAR NOT NULL UNIQUE,
    contract_month DATE NOT NULL,
    listing_date DATE,
    last_trade_date DATE,
    settlement_date DATE,
    status VARCHAR NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instrument_id)
        REFERENCES instruments(instrument_id)
);