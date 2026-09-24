from datetime import date

import pytest
from pydantic import ValidationError

from domain.broker_instruments import (
    AmbiguousBrokerInstrumentMapping,
    BrokerInstrumentMappingNotFound,
    BrokerInstrumentReference,
    BrokerInstrumentResolver,
)


def _reference(
    *,
    broker: str = "SINOPAC",
    instrument_id: int = 1,
    contract_id: int | None = None,
    product_code: str | None = "TXF",
    contract_code: str | None = None,
    effective_from: date | None = None,
    effective_to: date | None = None,
) -> BrokerInstrumentReference:
    return BrokerInstrumentReference(
        broker=broker,
        instrument_id=instrument_id,
        contract_id=contract_id,
        broker_product_code=product_code,
        broker_contract_code=contract_code,
        effective_from=effective_from,
        effective_to=effective_to,
    )


def test_valid_instrument_level_mapping_normalizes_broker() -> None:
    reference = _reference(broker=" sinopac ")

    assert reference.broker == "SINOPAC"
    assert reference.contract_id is None
    assert reference.broker_product_code == "TXF"


def test_valid_contract_level_mapping() -> None:
    reference = _reference(
        contract_id=101,
        product_code=None,
        contract_code="TX-synthetic-202601",
    )

    assert reference.contract_id == 101
    assert reference.broker_contract_code == "TX-synthetic-202601"


@pytest.mark.parametrize(
    ("field", "value"),
    [("instrument_id", 0), ("contract_id", 0)],
)
def test_ids_must_be_positive(field: str, value: int) -> None:
    values = {"instrument_id": 1, "contract_id": None}
    values[field] = value

    with pytest.raises(ValidationError):
        _reference(
            instrument_id=values["instrument_id"],
            contract_id=values["contract_id"],
        )


def test_blank_broker_is_rejected() -> None:
    with pytest.raises(ValidationError, match="broker must not be blank"):
        _reference(broker="  ")


def test_at_least_one_broker_code_is_required() -> None:
    with pytest.raises(ValidationError, match="broker_product_code or"):
        _reference(product_code=None, contract_code=None)


def test_effective_range_must_be_ordered() -> None:
    with pytest.raises(ValidationError, match="effective_from must not follow"):
        _reference(
            effective_from=date(2026, 2, 1),
            effective_to=date(2026, 1, 31),
        )


def test_effective_date_boundaries_are_inclusive() -> None:
    reference = _reference(
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 1, 31),
    )
    resolver = BrokerInstrumentResolver([reference])

    assert resolver.resolve(
        broker="SINOPAC",
        instrument_id=1,
        as_of_date=date(2026, 1, 1),
    ) is reference
    assert resolver.resolve(
        broker="SINOPAC",
        instrument_id=1,
        as_of_date=date(2026, 1, 31),
    ) is reference


def test_listed_contract_requires_exact_mapping_without_instrument_fallback() -> None:
    resolver = BrokerInstrumentResolver([_reference()])

    with pytest.raises(BrokerInstrumentMappingNotFound):
        resolver.resolve(
            broker="SINOPAC",
            instrument_id=1,
            contract_id=101,
            as_of_date=date(2026, 1, 15),
        )


def test_listed_contract_exact_mapping_is_resolved() -> None:
    instrument_reference = _reference()
    contract_reference = _reference(
        contract_id=101,
        product_code=None,
        contract_code="TX-synthetic-202601",
    )
    resolver = BrokerInstrumentResolver(
        [instrument_reference, contract_reference]
    )

    assert resolver.resolve(
        broker="sinopac",
        instrument_id=1,
        contract_id=101,
        as_of_date=date(2026, 1, 15),
    ) is contract_reference


def test_instrument_request_uses_only_instrument_level_mapping() -> None:
    instrument_reference = _reference()
    contract_reference = _reference(
        contract_id=101,
        product_code=None,
        contract_code="TX-synthetic-202601",
    )
    resolver = BrokerInstrumentResolver(
        [contract_reference, instrument_reference]
    )

    assert resolver.resolve(
        broker="SINOPAC",
        instrument_id=1,
        as_of_date=date(2026, 1, 15),
    ) is instrument_reference


def test_missing_mapping_is_explicit() -> None:
    with pytest.raises(BrokerInstrumentMappingNotFound, match="not found"):
        BrokerInstrumentResolver([]).resolve(
            broker="SINOPAC",
            instrument_id=1,
            as_of_date=date(2026, 1, 15),
        )


def test_overlapping_valid_mappings_are_ambiguous() -> None:
    resolver = BrokerInstrumentResolver(
        [
            _reference(effective_to=date(2026, 1, 31)),
            _reference(effective_from=date(2026, 1, 15)),
        ]
    )

    with pytest.raises(AmbiguousBrokerInstrumentMapping, match="multiple"):
        resolver.resolve(
            broker="SINOPAC",
            instrument_id=1,
            as_of_date=date(2026, 1, 20),
        )


@pytest.mark.parametrize(
    "references",
    [
        [_reference(broker="OTHER")],
        [_reference(instrument_id=2)],
        [_reference(effective_to=date(2026, 1, 14))],
        [_reference(effective_from=date(2026, 1, 16))],
    ],
)
def test_unrelated_expired_and_future_mappings_are_ignored(
    references: list[BrokerInstrumentReference],
) -> None:
    with pytest.raises(BrokerInstrumentMappingNotFound):
        BrokerInstrumentResolver(references).resolve(
            broker="SINOPAC",
            instrument_id=1,
            as_of_date=date(2026, 1, 15),
        )


def test_broker_codes_are_trimmed_without_case_coercion() -> None:
    reference = _reference(
        product_code=" TxF ",
        contract_code=" tx-Synthetic ",
    )

    assert reference.broker_product_code == "TxF"
    assert reference.broker_contract_code == "tx-Synthetic"


def test_native_broker_object_cannot_be_stored() -> None:
    with pytest.raises(ValidationError, match="native_contract"):
        BrokerInstrumentReference(
            broker="SINOPAC",
            instrument_id=1,
            broker_product_code="TXF",
            native_contract=object(),
        )


def test_reverse_contract_mapping_is_exact_case_sensitive_and_inclusive() -> None:
    reference = _reference(
        contract_id=101,
        product_code=None,
        contract_code="TX-synthetic-202601",
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 1, 31),
    )
    resolver = BrokerInstrumentResolver([reference])

    assert resolver.resolve_by_broker_contract_code(
        broker=" sinopac ",
        broker_contract_code=" TX-synthetic-202601 ",
        as_of_date=date(2026, 1, 31),
    ) is reference
    with pytest.raises(BrokerInstrumentMappingNotFound):
        resolver.resolve_by_broker_contract_code(
            broker="SINOPAC",
            broker_contract_code="tx-synthetic-202601",
            as_of_date=date(2026, 1, 31),
        )


def test_reverse_contract_mapping_never_falls_back_to_instrument_reference() -> None:
    resolver = BrokerInstrumentResolver([_reference(contract_code="TXF")])

    with pytest.raises(BrokerInstrumentMappingNotFound):
        resolver.resolve_by_broker_contract_code(
            broker="SINOPAC",
            broker_contract_code="TXF",
            as_of_date=date(2026, 1, 15),
        )


def test_reverse_contract_mapping_rejects_ambiguity() -> None:
    resolver = BrokerInstrumentResolver(
        [
            _reference(
                contract_id=101,
                product_code=None,
                contract_code="TX-synthetic-202601",
            ),
            _reference(
                contract_id=102,
                product_code=None,
                contract_code="TX-synthetic-202601",
            ),
        ]
    )

    with pytest.raises(AmbiguousBrokerInstrumentMapping):
        resolver.resolve_by_broker_contract_code(
            broker="SINOPAC",
            broker_contract_code="TX-synthetic-202601",
            as_of_date=date(2026, 1, 15),
        )
