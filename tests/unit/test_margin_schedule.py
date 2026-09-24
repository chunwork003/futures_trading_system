from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from domain.margins import (
    AmbiguousMarginScheduleError,
    MarginScheduleEntry,
    MarginScheduleResolver,
)


def make_margin_entry(**overrides: object) -> MarginScheduleEntry:
    values = {
        "margin_id": 1,
        "instrument_id": 10,
        "contract_id": None,
        "effective_date": date(2026, 1, 1),
        "currency": "TWD",
        "clearing_margin": Decimal("60000"),
        "maintenance_margin": Decimal("70000"),
        "initial_margin": Decimal("90000"),
        "source": "TAIFEX",
        "published_at": datetime(2025, 12, 31, 8, 0, tzinfo=timezone.utc),
    }
    values.update(overrides)
    return MarginScheduleEntry(**values)


def test_valid_instrument_level_margin_entry():
    entry = make_margin_entry()

    assert entry.instrument_id == 10
    assert entry.contract_id is None


def test_valid_contract_level_margin_entry():
    entry = make_margin_entry(contract_id=101)

    assert entry.contract_id == 101


@pytest.mark.parametrize("field", ["margin_id", "instrument_id", "contract_id"])
@pytest.mark.parametrize("value", [0, -1])
def test_margin_entry_requires_positive_ids(field: str, value: int):
    with pytest.raises(ValidationError):
        make_margin_entry(**{field: value})


@pytest.mark.parametrize(
    ("currency", "expected"),
    [("twd", "TWD"), (" USD ", "USD")],
)
def test_margin_currency_is_normalized(currency: str, expected: str):
    entry = make_margin_entry(currency=currency)

    assert entry.currency == expected


@pytest.mark.parametrize("currency", ["TW", "TWD1", "臺幣元"])
def test_margin_currency_requires_three_ascii_letters(currency: str):
    with pytest.raises(ValidationError):
        make_margin_entry(currency=currency)


def test_margin_values_are_decimal():
    entry = make_margin_entry(
        clearing_margin="60000.25",
        maintenance_margin="70000.50",
        initial_margin="90000.75",
    )

    assert entry.clearing_margin == Decimal("60000.25")
    assert entry.maintenance_margin == Decimal("70000.50")
    assert entry.initial_margin == Decimal("90000.75")
    assert isinstance(entry.initial_margin, Decimal)


@pytest.mark.parametrize(
    "field",
    ["clearing_margin", "maintenance_margin", "initial_margin"],
)
def test_margin_values_must_be_non_negative(field: str):
    with pytest.raises(ValidationError):
        make_margin_entry(**{field: Decimal("-0.01")})


def test_zero_margin_values_are_allowed():
    entry = make_margin_entry(
        clearing_margin=Decimal("0"),
        maintenance_margin=Decimal("0"),
        initial_margin=Decimal("0"),
    )

    assert entry.initial_margin == Decimal("0")


def test_margin_source_must_not_be_blank():
    with pytest.raises(ValidationError):
        make_margin_entry(source="   ")


def test_aware_published_at_is_accepted():
    published_at = datetime(2025, 12, 31, 8, 0, tzinfo=timezone.utc)

    assert make_margin_entry(published_at=published_at).published_at == published_at


def test_naive_published_at_is_rejected():
    with pytest.raises(ValidationError):
        make_margin_entry(published_at=datetime(2025, 12, 31, 8, 0))


def test_resolver_selects_exact_effective_date():
    entry = make_margin_entry(effective_date=date(2026, 1, 15))

    result = MarginScheduleResolver([entry]).resolve(
        instrument_id=10,
        as_of_date=date(2026, 1, 15),
    )

    assert result is entry


def test_resolver_selects_latest_previous_effective_date():
    previous = make_margin_entry(margin_id=1, effective_date=date(2026, 1, 1))
    latest = make_margin_entry(margin_id=2, effective_date=date(2026, 1, 10))

    result = MarginScheduleResolver([previous, latest]).resolve(
        instrument_id=10,
        as_of_date=date(2026, 1, 20),
    )

    assert result is latest


def test_resolver_does_not_select_future_entry():
    future = make_margin_entry(effective_date=date(2026, 2, 1))

    result = MarginScheduleResolver([future]).resolve(
        instrument_id=10,
        as_of_date=date(2026, 1, 31),
    )

    assert result is None


def test_contract_specific_margin_takes_precedence():
    instrument_entry = make_margin_entry(margin_id=1)
    contract_entry = make_margin_entry(margin_id=2, contract_id=101)

    result = MarginScheduleResolver([instrument_entry, contract_entry]).resolve(
        instrument_id=10,
        contract_id=101,
        as_of_date=date(2026, 1, 1),
    )

    assert result is contract_entry


def test_resolver_falls_back_to_instrument_margin():
    instrument_entry = make_margin_entry()

    result = MarginScheduleResolver([instrument_entry]).resolve(
        instrument_id=10,
        contract_id=999,
        as_of_date=date(2026, 1, 1),
    )

    assert result is instrument_entry


def test_resolver_returns_none_when_no_margin_exists():
    result = MarginScheduleResolver([]).resolve(
        instrument_id=10,
        as_of_date=date(2026, 1, 1),
    )

    assert result is None


def test_duplicate_schedule_key_is_rejected_explicitly():
    first = make_margin_entry(margin_id=1)
    duplicate = make_margin_entry(margin_id=2)

    with pytest.raises(AmbiguousMarginScheduleError):
        MarginScheduleResolver([first, duplicate])


def test_resolver_ignores_unrelated_instrument():
    expected = make_margin_entry(margin_id=1, instrument_id=10)
    unrelated = make_margin_entry(margin_id=2, instrument_id=20)

    result = MarginScheduleResolver([unrelated, expected]).resolve(
        instrument_id=10,
        as_of_date=date(2026, 1, 1),
    )

    assert result is expected


def test_later_schedule_supersedes_earlier_regardless_of_input_order():
    earlier = make_margin_entry(margin_id=1, effective_date=date(2026, 1, 1))
    later = make_margin_entry(margin_id=2, effective_date=date(2026, 1, 15))

    result = MarginScheduleResolver([later, earlier]).resolve(
        instrument_id=10,
        as_of_date=date(2026, 1, 20),
    )

    assert result is later


def test_margin_ordering_is_not_a_cross_market_invariant():
    entry = make_margin_entry(
        clearing_margin=Decimal("90000"),
        maintenance_margin=Decimal("70000"),
        initial_margin=Decimal("60000"),
    )

    assert entry.clearing_margin > entry.initial_margin
