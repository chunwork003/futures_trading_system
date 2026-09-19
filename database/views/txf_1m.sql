CREATE OR REPLACE VIEW txf_1m AS
SELECT *
FROM read_parquet(
    'data/parquet/bar/1m/TXF/**/*.parquet',
    hive_partitioning = true
);