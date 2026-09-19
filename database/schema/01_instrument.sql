CREATE TABLE IF NOT EXISTS instruments (
    instrument_id INTEGER PRIMARY KEY,
    symbol VARCHAR NOT NULL UNIQUE,
    name VARCHAR NOT NULL,
    asset_type VARCHAR NOT NULL,
    exchange VARCHAR NOT NULL,
    currency VARCHAR NOT NULL DEFAULT 'TWD',
    multiplier DOUBLE,
    tick_size DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO instruments (
    instrument_id,
    symbol,
    name,
    asset_type,
    exchange,
    currency,
    multiplier,
    tick_size
)
VALUES
    (1, 'TX', '臺股期貨', 'FUTURES', 'TAIFEX', 'TWD', 200, 1),
    (2, 'MTX', '小型臺指期貨', 'FUTURES', 'TAIFEX', 'TWD', 50, 1),
    (3, 'TMF', '微型臺指期貨', 'FUTURES', 'TAIFEX', 'TWD', 10, 1),
    (4, 'TWII', '發行量加權股價指數', 'INDEX', 'TWSE', 'TWD', NULL, 1);