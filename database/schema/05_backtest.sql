CREATE TABLE IF NOT EXISTS backtest_runs (
    run_id UUID PRIMARY KEY,
    strategy_name VARCHAR NOT NULL,
    strategy_version VARCHAR NOT NULL,
    symbol VARCHAR NOT NULL,
    timeframe VARCHAR NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DOUBLE NOT NULL,
    parameters JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS trades (
    trade_id BIGINT PRIMARY KEY,
    run_id UUID NOT NULL,

    symbol VARCHAR NOT NULL,
    contract VARCHAR NOT NULL,

    entry_time TIMESTAMP NOT NULL,
    entry_price DOUBLE NOT NULL,
    entry_side VARCHAR NOT NULL,
    entry_quantity INTEGER NOT NULL,

    exit_time TIMESTAMP,
    exit_price DOUBLE,

    gross_pnl DOUBLE,
    commission DOUBLE,
    slippage DOUBLE,
    net_pnl DOUBLE,

    exit_reason VARCHAR,

    FOREIGN KEY (run_id)
        REFERENCES backtest_runs(run_id)
);


CREATE TABLE IF NOT EXISTS equity_curve (
    run_id UUID NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    equity DOUBLE NOT NULL,
    cash DOUBLE,
    unrealized_pnl DOUBLE,
    realized_pnl DOUBLE,
    drawdown DOUBLE,

    FOREIGN KEY (run_id)
        REFERENCES backtest_runs(run_id)
);