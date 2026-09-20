from ingestion.github_txf_stream import (
    iter_txf_sql_batches,
    iter_txf_sql_rows,
)


def _write_sample(path):
    path.write_text(
        """COPY futures_1min (datetime, product_id, open, high, low, close, volume, trading_date, is_synthetic) FROM stdin;
2026-01-02 08:45:00\tTXFR1\t100.00\t101.00\t99.00\t100.50\t10\t2026-01-02\tf
2026-01-02 08:46:00\tTXFR1\t100.50\t102.00\t100.00\t101.50\t20\t2026-01-02\tf
2026-01-02 08:47:00\tTXFR1\t101.50\t103.00\t101.00\t102.50\t30\t2026-01-02\tf
\\.
""",
        encoding="utf-8",
    )


def test_iter_txf_sql_rows(tmp_path):
    path = tmp_path / "sample.sql"
    _write_sample(path)

    rows = list(iter_txf_sql_rows(path))

    assert len(rows) == 3
    assert rows[0][0] == "2026-01-02 08:45:00"
    assert rows[0][1] == "TXFR1"


def test_iter_txf_sql_batches(tmp_path):
    path = tmp_path / "sample.sql"
    _write_sample(path)

    batches = list(
        iter_txf_sql_batches(
            path,
            batch_size=2,
        )
    )

    assert len(batches) == 2
    assert batches[0].height == 2
    assert batches[1].height == 1

    assert batches[0]["symbol"].to_list() == [
        "TXF",
        "TXF",
    ]

    assert batches[0]["timeframe"].to_list() == [
        "1m",
        "1m",
    ]
