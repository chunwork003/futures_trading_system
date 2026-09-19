CREATE TABLE IF NOT EXISTS trading_calendar (
    trade_date DATE PRIMARY KEY,

    is_trading_day BOOLEAN NOT NULL,

    day_session BOOLEAN NOT NULL DEFAULT FALSE,
    night_session BOOLEAN NOT NULL DEFAULT FALSE,

    day_open TIME,
    day_close TIME,

    night_open TIME,
    night_close TIME,

    notes VARCHAR,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);