from decimal import Decimal

import pytest
from pydantic import ValidationError

from domain.instruments import (
    AssetType,
    Instrument,
    InstrumentSpec,
    InstrumentStatus,
)


# Source: TAIFEX official contract specification.
# Verified: 2026-09-24.
TAIFEX_V1_PRODUCT_SPECS = (
    ("TX", Decimal("200"), Decimal("1")),
    ("MTX", Decimal("50"), Decimal("1")),
    ("TMF", Decimal("10"), Decimal("1")),
)


@pytest.mark.parametrize(
    ("canonical_symbol", "multiplier", "tick_size"),
    TAIFEX_V1_PRODUCT_SPECS,
)
def test_taifex_v1_instrument_semantics_are_representable(
    canonical_symbol: str,
    multiplier: Decimal,
    tick_size: Decimal,
):
    spec = InstrumentSpec(
        instrument_id=1,
        canonical_symbol=canonical_symbol,
        name=canonical_symbol,
        asset_type=AssetType.FUTURE,
        exchange="TAIFEX",
        currency="TWD",
        multiplier=multiplier,
        tick_size=tick_size,
        trading_session_ref="TAIFEX-FUTURES",
    )

    assert spec.linear_tick_value == multiplier * tick_size


def test_instrument_spec_normalizes_identifiers_currency_and_legacy_futures():
    spec = InstrumentSpec(
        instrument_id=1,
        canonical_symbol=" tx ",
        name="臺股期貨",
        asset_type="futures",
        exchange=" taifex ",
        currency=" twd ",
        multiplier="200",
        tick_size="1",
    )

    assert spec.canonical_symbol == "TX"
    assert spec.asset_type is AssetType.FUTURE
    assert spec.exchange == "TAIFEX"
    assert spec.currency == "TWD"
    assert spec.status is InstrumentStatus.ACTIVE


@pytest.mark.parametrize(
    ("currency", "expected"),
    [
        ("twd", "TWD"),
        ("USD", "USD"),
    ],
)
def test_instrument_spec_normalizes_valid_ascii_currency(
    currency: str,
    expected: str,
):
    spec = InstrumentSpec(
        instrument_id=1,
        canonical_symbol="TEST",
        name="Test Instrument",
        asset_type="FUTURES",
        exchange="TEST",
        currency=currency,
    )

    assert spec.currency == expected


@pytest.mark.parametrize("asset_type", ["FUTURE", "FUTURES", "STOCK", "ETF", "INDEX"])
def test_instrument_spec_supports_required_asset_types(asset_type: str):
    spec = InstrumentSpec(
        instrument_id=1,
        canonical_symbol="TEST",
        name="Test Instrument",
        asset_type=asset_type,
        exchange="TEST",
    )

    expected = AssetType.FUTURE if asset_type in {"FUTURE", "FUTURES"} else AssetType(asset_type)
    assert spec.asset_type is expected


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("instrument_id", 0),
        ("canonical_symbol", " "),
        ("name", " "),
        ("multiplier", 0),
        ("tick_size", -1),
        ("currency", "NTDOLLAR"),
        ("currency", "US"),
        ("currency", "臺幣元"),
    ],
)
def test_instrument_spec_rejects_invalid_values(field: str, value: object):
    values = {
        "instrument_id": 1,
        "canonical_symbol": "TX",
        "name": "臺股期貨",
        "asset_type": "FUTURES",
        "exchange": "TAIFEX",
        "currency": "TWD",
        "multiplier": Decimal("200"),
        "tick_size": Decimal("1"),
    }
    values[field] = value

    with pytest.raises(ValidationError):
        InstrumentSpec(**values)


def test_linear_tick_value_is_none_when_specification_is_incomplete():
    spec = InstrumentSpec(
        instrument_id=1,
        canonical_symbol="TWII",
        name="臺灣加權股價指數",
        asset_type=AssetType.INDEX,
        exchange="TWSE",
        multiplier=None,
        tick_size=Decimal("1"),
    )

    assert spec.linear_tick_value is None


def test_legacy_instrument_import_and_conversion_remain_compatible():
    instrument = Instrument(
        instrument_id=1,
        symbol="TX",
        name="臺股期貨",
        asset_type="FUTURES",
        exchange="TAIFEX",
        multiplier=200.0,
        tick_size=1.0,
    )

    spec = instrument.to_spec(trading_session_ref="TAIFEX-FUTURES")

    assert instrument.symbol == "TX"
    assert spec.canonical_symbol == instrument.symbol
    assert spec.multiplier == Decimal("200.0")
    assert spec.tick_size == Decimal("1.0")
    assert spec.linear_tick_value == Decimal("200.00")
