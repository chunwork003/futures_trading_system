from datetime import date, datetime

import polars as pl
import pytest

from ingestion.base import DataSource
from ingestion.metadata import SourceMetadata
from ingestion.request import DataRequest
from ingestion.txf import TXFDataSource


def test_txf_datasource_implements_interface():
    source = TXFDataSource()

    assert isinstance(source, DataSource)
    assert source.source_name == "txf"


def test_data_request():
    request = DataRequest(
        symbol="TXF",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )

    assert request.symbol == "TXF"
    assert request.timeframe == "1m"


def test_data_request_rejects_invalid_date_range():
    with pytest.raises(ValueError):
        DataRequest(
            symbol="TXF",
            start_date=date(2026, 2, 1),
            end_date=date(2026, 1, 1),
        )


def test_source_metadata():
    metadata = SourceMetadata(
        source="github",
        source_file="data_TXFR1_2026.sql",
        source_version="v2",
        source_hash="abc123",
    )

    assert metadata.source == "github"
    assert metadata.source_file == "data_TXFR1_2026.sql"
    assert metadata.source_version == "v2"


def test_domain_bar_is_canonical_schema():
    from domain.bars import Bar

    bar = Bar(
        timestamp=datetime(2026, 1, 2, 8, 45),
        trade_date=date(2026, 1, 2),
        symbol="TXF",
        contract="TXFR1",
        timeframe="1m",
        open=100.0,
        high=101.0,
        low=99.0,
        close=100.5,
        volume=10,
        session="DAY",
        source="github",
    )

    assert bar.symbol == "TXF"
    assert bar.timeframe == "1m"
    assert bar.open == 100.0
    assert bar.volume == 10


def test_datasource_download_not_implemented_yet():
    source = TXFDataSource()

    with pytest.raises(NotImplementedError):
        source.download(
            date(2026, 1, 1),
            date(2026, 1, 2),
        )
