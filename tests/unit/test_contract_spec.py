from datetime import date

import pytest
from pydantic import ValidationError

from domain.contracts import (
    Contract,
    ContractSeriesType,
    ContractSpec,
    ContractStatus,
)


def make_contract_spec(**overrides: object) -> ContractSpec:
    values = {
        "contract_id": 1,
        "instrument_id": 10,
        "canonical_code": "TX202601",
        "series_type": ContractSeriesType.MONTHLY,
        "expiration_date": date(2026, 1, 21),
        "contract_month": date(2026, 1, 1),
        "listing_date": date(2025, 1, 2),
        "last_trade_date": date(2026, 1, 21),
        "settlement_date": date(2026, 1, 21),
        "status": ContractStatus.ACTIVE,
    }
    values.update(overrides)
    return ContractSpec(**values)


def test_monthly_contract_spec_uses_typed_month_identity():
    spec = make_contract_spec()

    assert spec.series_type is ContractSeriesType.MONTHLY
    assert spec.contract_month == date(2026, 1, 1)


def test_weekly_contract_spec_does_not_require_contract_month():
    weekly_expiration = date(2026, 1, 9)

    spec = make_contract_spec(
        canonical_code="MTX-W-2026-01-09",
        series_type=ContractSeriesType.WEEKLY,
        contract_month=None,
        expiration_date=weekly_expiration,
        last_trade_date=weekly_expiration,
        settlement_date=weekly_expiration,
    )

    assert spec.series_type is ContractSeriesType.WEEKLY
    assert spec.contract_month is None
    assert spec.expiration_date == weekly_expiration
    assert spec.last_trade_date == weekly_expiration


@pytest.mark.parametrize("series_type", ["MONTHLY", "QUARTERLY", "WEEKLY", "OTHER"])
def test_contract_spec_supports_listed_series_types(series_type: str):
    spec = make_contract_spec(series_type=series_type)

    assert spec.series_type is ContractSeriesType(series_type)


def test_continuous_series_is_not_a_listed_contract_series_type():
    with pytest.raises(ValidationError):
        make_contract_spec(series_type="CONTINUOUS")


@pytest.mark.parametrize("field", ["contract_id", "instrument_id"])
@pytest.mark.parametrize("value", [0, -1])
def test_contract_spec_requires_positive_ids(field: str, value: int):
    with pytest.raises(ValidationError):
        make_contract_spec(**{field: value})


def test_contract_spec_rejects_blank_canonical_code():
    with pytest.raises(ValidationError):
        make_contract_spec(canonical_code="   ")


def test_contract_month_uses_first_day_as_month_identity():
    with pytest.raises(ValidationError):
        make_contract_spec(contract_month=date(2026, 1, 2))


@pytest.mark.parametrize(
    "overrides",
    [
        {"listing_date": date(2026, 1, 22)},
        {
            "last_trade_date": date(2026, 1, 22),
            "settlement_date": date(2026, 1, 21),
        },
    ],
)
def test_contract_spec_rejects_reversed_lifecycle_dates(overrides: dict):
    with pytest.raises(ValidationError):
        make_contract_spec(**overrides)


def test_contract_spec_allows_distinct_ordered_lifecycle_dates():
    spec = make_contract_spec(
        last_trade_date=date(2026, 1, 20),
        expiration_date=date(2026, 1, 21),
        settlement_date=date(2026, 1, 22),
    )

    assert spec.last_trade_date != spec.expiration_date
    assert spec.expiration_date != spec.settlement_date


def test_contract_spec_does_not_assume_expiration_settlement_ordering():
    spec = make_contract_spec(
        last_trade_date=date(2026, 1, 20),
        settlement_date=date(2026, 1, 21),
        expiration_date=date(2026, 1, 22),
    )

    assert spec.expiration_date > spec.settlement_date


def test_contract_spec_allows_optional_lifecycle_dates():
    spec = make_contract_spec(
        expiration_date=None,
        listing_date=None,
        last_trade_date=None,
        settlement_date=None,
    )

    assert spec.expiration_date is None
    assert spec.listing_date is None
    assert spec.last_trade_date is None
    assert spec.settlement_date is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, None),
        ("", None),
        ("  ", None),
        (" TAIFEX-NIGHT ", "TAIFEX-NIGHT"),
    ],
)
def test_session_override_reference_normalization(
    value: str | None,
    expected: str | None,
):
    spec = make_contract_spec(session_override_ref=value)

    assert spec.session_override_ref == expected


@pytest.mark.parametrize("status", ["ACTIVE", "EXPIRED", "INACTIVE"])
def test_contract_status_compatibility(status: str):
    spec = make_contract_spec(status=status.lower())

    assert spec.status is ContractStatus(status)


def test_unknown_legacy_contract_status_is_rejected_explicitly():
    legacy = Contract(
        contract_id=1,
        instrument_id=10,
        contract_code="TX202601",
        contract_month=date(2026, 1, 1),
        status="UNKNOWN",
    )

    with pytest.raises(ValidationError):
        legacy.to_spec()


def test_legacy_contract_converts_without_changing_existing_fields():
    legacy = Contract(
        contract_id=1,
        instrument_id=10,
        contract_code="TX202601",
        contract_month=date(2026, 1, 1),
        listing_date=date(2025, 1, 2),
        last_trade_date=date(2026, 1, 21),
        settlement_date=date(2026, 1, 21),
        status="ACTIVE",
    )

    spec = legacy.to_spec()

    assert legacy.contract_code == "TX202601"
    assert spec.canonical_code == legacy.contract_code
    assert spec.contract_month == legacy.contract_month
    assert spec.status is ContractStatus.ACTIVE


def test_legacy_contract_defaults_to_monthly_as_compatibility_assumption():
    legacy = Contract(
        contract_id=1,
        instrument_id=10,
        contract_code="TX202601",
        contract_month=date(2026, 1, 1),
    )

    spec = legacy.to_spec()

    assert spec.series_type is ContractSeriesType.MONTHLY
    assert spec.expiration_date is None
