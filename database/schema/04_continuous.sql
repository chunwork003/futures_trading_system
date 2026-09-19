CREATE TABLE IF NOT EXISTS continuous_contracts (
    continuous_id BIGINT PRIMARY KEY,
    instrument_id INTEGER NOT NULL,
    continuous_code VARCHAR NOT NULL UNIQUE,
    rollover_rule VARCHAR NOT NULL,
    adjustment_method VARCHAR NOT NULL,
    description VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instrument_id)
        REFERENCES instruments(instrument_id)
);