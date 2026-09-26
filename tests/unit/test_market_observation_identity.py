from __future__ import annotations

from dataclasses import fields
from datetime import date, datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import re

import pytest

from domain.market_observation import (
    CanonicalMarketObservationContent,
    MarketObservationContentFingerprint,
    MarketObservationContractError,
    MarketObservationLogicalKey,
    MarketObservationRevisionId,
    build_market_observation_revision_id,
    canonicalize_market_observation_content,
    canonicalize_market_observation_logical_key,
    normalize_market_observation_timeframe,
)


FIXTURE_PATH = (
    Path(__file__).parents[1]
    / "fixtures"
    / "market_observation_golden_vectors_v1.json"
)

GOLDEN = json.loads(
    FIXTURE_PATH.read_text(encoding="utf-8")
)

VECTORS = GOLDEN["vectors"]


def _vector(name: str) -> dict[str, object]:
    return next(
        item
        for item in VECTORS
        if item["name"] == name
    )


def _key(vector: dict[str, object]) -> MarketObservationLogicalKey:
    identity = vector["identity"]

    return canonicalize_market_observation_logical_key(
        instrument_id=identity["instrument_id"],
        contract_id=identity["contract_id"],
        requires_contract_id=identity["requires_contract_id"],
        timeframe=identity["timeframe"],
        interval_start_at=datetime.fromisoformat(
            identity["interval_start_at"]
        ),
    )


def _content(
    vector: dict[str, object],
) -> CanonicalMarketObservationContent:
    content = vector["content"]

    return canonicalize_market_observation_content(
        open=content["open"],
        high=content["high"],
        low=content["low"],
        close=content["close"],
        volume=content["volume"],
        amount=content["amount"],
        trade_count=content["trade_count"],
        tick_count=content["tick_count"],
        trade_date=date.fromisoformat(
            content["trade_date"]
        ),
        session_ref=content["session_ref"],
    )


def _identity(
    vector: dict[str, object],
) -> tuple[
    MarketObservationLogicalKey,
    MarketObservationContentFingerprint,
    MarketObservationRevisionId,
]:
    logical_key = _key(vector)
    content = _content(vector)
    fingerprint = content.content_fingerprint
    revision_id = build_market_observation_revision_id(
        logical_key=logical_key,
        content_fingerprint=fingerprint,
    )

    return logical_key, fingerprint, revision_id


@pytest.mark.parametrize(
    "vector",
    VECTORS,
    ids=lambda item: item["name"],
)
def test_cross_language_golden_vectors_are_fixed_literals(
    vector: dict[str, object],
) -> None:
    expected = vector["expected"]

    logical_key, fingerprint, revision_id = _identity(vector)

    assert logical_key.timeframe == expected["timeframe"]
    assert (
        logical_key.interval_start_at_lexical
        == expected["interval_start_at"]
    )
    assert fingerprint.value == expected["content_fingerprint"]
    assert revision_id.value == expected["revision_id"]


def test_golden_fixture_contains_fixed_expected_hashes() -> None:
    assert GOLDEN["schema"] == "market-observation-golden-vectors-v1"
    assert GOLDEN["identity_schema_version"] == 1
    assert GOLDEN["content_schema_version"] == 1

    for vector in VECTORS:
        expected = vector["expected"]

        assert re.fullmatch(
            r"[0-9a-f]{64}",
            expected["content_fingerprint"],
        )
        assert re.fullmatch(
            r"mor1_[0-9a-f]{64}",
            expected["revision_id"],
        )


def test_timezone_decimal_timeframe_and_replay_equivalence() -> None:
    names = (
        "listed_contract_utc",
        "equivalent_timezone_and_decimal",
        "decimal_trailing_zero_replay",
        "timeframe_60s_equivalent",
        "same_content_replay",
    )

    identities = [
        _identity(_vector(name))
        for name in names
    ]

    first_key, first_fingerprint, first_revision_id = identities[0]

    for logical_key, fingerprint, revision_id in identities[1:]:
        assert logical_key == first_key
        assert fingerprint == first_fingerprint
        assert revision_id == first_revision_id


def test_negative_zero_normalizes_to_zero() -> None:
    content = _content(
        _vector("negative_zero_normalization")
    )

    assert content.open == Decimal("0")
    assert content.low == Decimal("0")
    assert content.close == Decimal("0")
    assert content.amount == Decimal("0")


def test_legitimate_non_contract_context_preserves_canonical_null() -> None:
    logical_key, _, revision_id = _identity(
        _vector("legitimate_null_contract")
    )

    assert logical_key.contract_id is None
    assert revision_id.value.startswith("mor1_")


def test_market_data_change_changes_fingerprint_and_revision_id() -> None:
    base = _identity(_vector("listed_contract_utc"))
    changed = _identity(_vector("market_data_change"))

    assert base[0] == changed[0]
    assert base[1] != changed[1]
    assert base[2] != changed[2]


def test_classification_only_change_changes_fingerprint_and_revision_id() -> None:
    base = _identity(_vector("listed_contract_utc"))
    changed = _identity(_vector("classification_only_change"))

    assert base[0] == changed[0]
    assert base[1] != changed[1]
    assert base[2] != changed[2]


def test_revision_id_has_exact_opaque_format() -> None:
    _, _, revision_id = _identity(
        _vector("listed_contract_utc")
    )

    assert re.fullmatch(
        r"mor1_[0-9a-f]{64}",
        revision_id.value,
    )


def test_24h_is_not_silently_equated_to_calendar_1d() -> None:
    assert normalize_market_observation_timeframe("24h") == "24h"
    assert normalize_market_observation_timeframe("1d") == "1d"

    common = {
        "instrument_id": 2,
        "contract_id": None,
        "requires_contract_id": False,
        "interval_start_at": datetime(
            2026,
            9,
            25,
            0,
            tzinfo=timezone.utc,
        ),
    }

    hourly = canonicalize_market_observation_logical_key(
        **common,
        timeframe="24h",
    )
    daily = canonicalize_market_observation_logical_key(
        **common,
        timeframe="1d",
    )

    assert hourly != daily


def test_listed_contract_context_requires_contract_id() -> None:
    with pytest.raises(
        MarketObservationContractError,
        match="contract_id is required",
    ):
        canonicalize_market_observation_logical_key(
            instrument_id=1,
            contract_id=None,
            requires_contract_id=True,
            timeframe="1m",
            interval_start_at=datetime(
                2026,
                9,
                25,
                1,
                tzinfo=timezone.utc,
            ),
        )


def test_naive_interval_time_is_rejected() -> None:
    with pytest.raises(
        MarketObservationContractError,
        match="timezone-aware",
    ):
        canonicalize_market_observation_logical_key(
            instrument_id=1,
            contract_id=101,
            requires_contract_id=True,
            timeframe="1m",
            interval_start_at=datetime(
                2026,
                9,
                25,
                1,
            ),
        )


@pytest.mark.parametrize(
    "instrument_id",
    [
        0,
        -1,
        True,
        1.0,
        "1",
    ],
)
def test_invalid_instrument_id_is_rejected(
    instrument_id: object,
) -> None:
    with pytest.raises(MarketObservationContractError):
        canonicalize_market_observation_logical_key(
            instrument_id=instrument_id,
            contract_id=101,
            requires_contract_id=True,
            timeframe="1m",
            interval_start_at=datetime(
                2026,
                9,
                25,
                1,
                tzinfo=timezone.utc,
            ),
        )


@pytest.mark.parametrize(
    "contract_id",
    [
        0,
        -1,
        True,
        1.0,
        "101",
    ],
)
def test_invalid_contract_id_is_rejected(
    contract_id: object,
) -> None:
    with pytest.raises(MarketObservationContractError):
        canonicalize_market_observation_logical_key(
            instrument_id=1,
            contract_id=contract_id,
            requires_contract_id=True,
            timeframe="1m",
            interval_start_at=datetime(
                2026,
                9,
                25,
                1,
                tzinfo=timezone.utc,
            ),
        )


@pytest.mark.parametrize(
    "timeframe",
    [
        "",
        " ",
        "0m",
        "-1m",
        "abc",
        "1w",
    ],
)
def test_invalid_timeframe_is_rejected(
    timeframe: str,
) -> None:
    with pytest.raises(MarketObservationContractError):
        canonicalize_market_observation_logical_key(
            instrument_id=1,
            contract_id=101,
            requires_contract_id=True,
            timeframe=timeframe,
            interval_start_at=datetime(
                2026,
                9,
                25,
                1,
                tzinfo=timezone.utc,
            ),
        )


def test_timeframe_case_whitespace_and_60s_normalize_to_1m() -> None:
    assert normalize_market_observation_timeframe("1m") == "1m"
    assert normalize_market_observation_timeframe(" 1M ") == "1m"
    assert normalize_market_observation_timeframe("60s") == "1m"


@pytest.mark.parametrize(
    "bad_value",
    [
        1.0,
        float("-0.0"),
    ],
)
def test_raw_float_market_numeric_is_rejected(
    bad_value: float,
) -> None:
    with pytest.raises(
        MarketObservationContractError,
        match="exact decimal",
    ):
        canonicalize_market_observation_content(
            open=bad_value,
            high="2",
            low="0",
            close="1",
            volume=1,
            amount=None,
            trade_count=None,
            tick_count=None,
            trade_date=date(2026, 9, 25),
            session_ref=None,
        )


@pytest.mark.parametrize(
    "bad_value",
    [
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
)
def test_non_finite_decimal_is_rejected(
    bad_value: Decimal,
) -> None:
    with pytest.raises(
        MarketObservationContractError,
        match="finite",
    ):
        canonicalize_market_observation_content(
            open=bad_value,
            high="2",
            low="0",
            close="1",
            volume=1,
            amount=None,
            trade_count=None,
            tick_count=None,
            trade_date=date(2026, 9, 25),
            session_ref=None,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "volume",
        "trade_count",
        "tick_count",
    ],
)
def test_bool_count_evidence_is_rejected(
    field_name: str,
) -> None:
    values = {
        "open": "1",
        "high": "2",
        "low": "0",
        "close": "1",
        "volume": 1,
        "amount": None,
        "trade_count": 1,
        "tick_count": 1,
        "trade_date": date(2026, 9, 25),
        "session_ref": None,
    }
    values[field_name] = True

    with pytest.raises(MarketObservationContractError):
        canonicalize_market_observation_content(**values)


@pytest.mark.parametrize(
    "field_name",
    [
        "volume",
        "trade_count",
        "tick_count",
    ],
)
def test_negative_count_evidence_is_rejected(
    field_name: str,
) -> None:
    values = {
        "open": "1",
        "high": "2",
        "low": "0",
        "close": "1",
        "volume": 1,
        "amount": None,
        "trade_count": 1,
        "tick_count": 1,
        "trade_date": date(2026, 9, 25),
        "session_ref": None,
    }
    values[field_name] = -1

    with pytest.raises(MarketObservationContractError):
        canonicalize_market_observation_content(**values)


def test_bool_price_evidence_is_rejected() -> None:
    with pytest.raises(MarketObservationContractError):
        canonicalize_market_observation_content(
            open=True,
            high="2",
            low="0",
            close="1",
            volume=1,
            amount=None,
            trade_count=None,
            tick_count=None,
            trade_date=date(2026, 9, 25),
            session_ref=None,
        )


def test_blank_session_reference_is_rejected() -> None:
    with pytest.raises(
        MarketObservationContractError,
        match="session_ref must not be blank",
    ):
        canonicalize_market_observation_content(
            open="1",
            high="2",
            low="0",
            close="1",
            volume=1,
            amount=None,
            trade_count=None,
            tick_count=None,
            trade_date=date(2026, 9, 25),
            session_ref="   ",
        )


def test_datetime_is_not_accepted_as_trade_date() -> None:
    with pytest.raises(
        MarketObservationContractError,
        match="trade_date must be a date",
    ):
        canonicalize_market_observation_content(
            open="1",
            high="2",
            low="0",
            close="1",
            volume=1,
            amount=None,
            trade_count=None,
            tick_count=None,
            trade_date=datetime(
                2026,
                9,
                25,
                tzinfo=timezone.utc,
            ),
            session_ref=None,
        )


@pytest.mark.parametrize(
    "value",
    [
        "",
        "ABC",
        "A" * 64,
        "0" * 63,
        "0" * 65,
    ],
)
def test_content_fingerprint_value_object_rejects_invalid_format(
    value: str,
) -> None:
    with pytest.raises(MarketObservationContractError):
        MarketObservationContentFingerprint(value)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "mor1_ABC",
        "mor1_" + ("A" * 64),
        "mor2_" + ("0" * 64),
        "mor1_" + ("0" * 63),
    ],
)
def test_revision_id_value_object_rejects_invalid_format(
    value: str,
) -> None:
    with pytest.raises(MarketObservationContractError):
        MarketObservationRevisionId(value)


def test_logical_key_contains_only_frozen_identity_fields() -> None:
    assert [
        field.name
        for field in fields(MarketObservationLogicalKey)
    ] == [
        "instrument_id",
        "contract_id",
        "timeframe",
        "interval_start_at",
    ]


def test_content_contract_excludes_source_and_feature_provenance() -> None:
    assert [
        field.name
        for field in fields(CanonicalMarketObservationContent)
    ] == [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount",
        "trade_count",
        "tick_count",
        "trade_date",
        "session_ref",
    ]


def test_static_identity_contract_excludes_json_and_revision_authority() -> None:
    source = Path(
        "domain/market_observation.py"
    ).read_text(encoding="utf-8-sig")

    assert "import json" not in source
    assert "json.dumps" not in source
    assert "revision_seq" not in source

    logical_fields = {
        field.name
        for field in fields(MarketObservationLogicalKey)
    }

    assert "symbol" not in logical_fields
    assert "exchange" not in logical_fields
    assert "source" not in logical_fields
    assert "provenance" not in logical_fields
