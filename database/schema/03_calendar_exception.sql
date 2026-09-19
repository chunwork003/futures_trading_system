CREATE TABLE IF NOT EXISTS calendar_exceptions (
    exception_id BIGINT PRIMARY KEY,

    trade_date DATE NOT NULL,

    instrument_id INTEGER,

    session_type VARCHAR NOT NULL,

    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,

    open_time TIME,

    close_time TIME,

    reason VARCHAR,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (instrument_id)
        REFERENCES instruments(instrument_id)
);