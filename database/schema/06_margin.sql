CREATE TABLE IF NOT EXISTS margin_rates (
    margin_id BIGINT PRIMARY KEY,

    instrument_id INTEGER NOT NULL,

    effective_date DATE NOT NULL,

    clearing_margin DOUBLE NOT NULL,

    maintenance_margin DOUBLE NOT NULL,

    initial_margin DOUBLE NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (instrument_id)
        REFERENCES instruments(instrument_id),

    UNIQUE (
        instrument_id,
        effective_date
    )
);