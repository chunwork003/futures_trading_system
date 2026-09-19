CREATE OR REPLACE VIEW mxf_1m AS
SELECT *
FROM read_parquet(
    'data/parquet/bar/1m/MXF/**/*.parquet',
    hive_partitioning = true
);