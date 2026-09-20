CREATE OR REPLACE VIEW txf_1m AS
SELECT
    timestamp,
    trade_date,
    symbol,
    contract,
    timeframe,
    open,
    high,
    low,
    close,
    volume,
    session,
    source
FROM read_parquet(
    'data/parquet/bar/1m/TXF/**/*.parquet',
    hive_partitioning = true
);
