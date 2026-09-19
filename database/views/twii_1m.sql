CREATE OR REPLACE VIEW twii_1m AS
SELECT *
FROM read_parquet(
    'data/parquet/bar/1m/TWII/**/*.parquet',
    hive_partitioning = true
);