CREATE TABLE IF NOT EXISTS github_futures_1m (
    datetime TIMESTAMP NOT NULL,
    product_id VARCHAR NOT NULL,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume BIGINT,
    trading_date DATE,
    is_synthetic BOOLEAN NOT NULL DEFAULT FALSE,
    source_file VARCHAR,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
