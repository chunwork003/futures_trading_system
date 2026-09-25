from datetime import date

import pytest
from pydantic import ValidationError

from adapters.capabilities import (
    BrokerCapability,
    BrokerCapabilityEvidence,
    BrokerCapabilityMatrix,
    BrokerCapabilitySupport,
    BrokerCapabilityUnavailableError,
    BrokerVerificationMode,
    get_broker_capability,
    require_broker_capability,
)
from adapters.sinopac.capabilities import SINOPAC_CAPABILITY_MATRIX


def evidence(
    capability: BrokerCapability = BrokerCapability.ACCOUNT_QUERY,
    *,
    support: BrokerCapabilitySupport = BrokerCapabilitySupport.SUPPORTED,
    source_ids: tuple[str, ...] = ("SRC-1",),
    modes: tuple[BrokerVerificationMode, ...] = (
        BrokerVerificationMode.DOCUMENTATION,
    ),
) -> BrokerCapabilityEvidence:
    return BrokerCapabilityEvidence(
        capability=capability,
        support=support,
        source_ids=source_ids,
        verification_modes=modes,
        sdk_version=" 1.0 ",
        verified_on=date(2026, 9, 25),
        note=" reviewed ",
    )


def test_enums_have_exact_frozen_values() -> None:
    assert [item.value for item in BrokerCapability] == [
        "ACCOUNT_QUERY", "POSITION_QUERY", "ORDER_PLACE", "ORDER_UPDATE",
        "ORDER_CANCEL", "ORDER_STATUS", "TRADE_LIST", "ORDER_DEAL_EVENT",
    ]
    assert [item.value for item in BrokerCapabilitySupport] == [
        "SUPPORTED", "UNSUPPORTED", "UNKNOWN",
    ]
    assert [item.value for item in BrokerVerificationMode] == [
        "DOCUMENTATION", "FAKE", "SIMULATION", "PRODUCTION",
    ]


def test_evidence_is_immutable_extra_forbid_and_normalized() -> None:
    item = evidence(source_ids=(" SRC-1 ",))
    assert item.source_ids == ("SRC-1",)
    assert item.sdk_version == "1.0"
    assert item.note == "reviewed"
    with pytest.raises(ValidationError):
        item.note = "changed"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        BrokerCapabilityEvidence(**item.model_dump(), unexpected=True)


@pytest.mark.parametrize("source_ids", [("",), ("   ",), ("SRC-1", " SRC-1 ")])
def test_source_ids_reject_blank_or_duplicate(source_ids: tuple[str, ...]) -> None:
    with pytest.raises(ValidationError):
        evidence(source_ids=source_ids)


def test_verification_modes_reject_duplicate_and_use_enum_order() -> None:
    with pytest.raises(ValidationError):
        evidence(modes=(BrokerVerificationMode.FAKE, BrokerVerificationMode.FAKE))
    item = evidence(modes=(BrokerVerificationMode.PRODUCTION, BrokerVerificationMode.DOCUMENTATION))
    assert item.verification_modes == (
        BrokerVerificationMode.DOCUMENTATION,
        BrokerVerificationMode.PRODUCTION,
    )


@pytest.mark.parametrize("field", ["sdk_version", "note"])
def test_optional_text_rejects_blank(field: str) -> None:
    values = evidence().model_dump()
    values[field] = "  "
    with pytest.raises(ValidationError):
        BrokerCapabilityEvidence(**values)


@pytest.mark.parametrize("support", [BrokerCapabilitySupport.SUPPORTED, BrokerCapabilitySupport.UNSUPPORTED])
def test_known_support_requires_source_evidence(support: BrokerCapabilitySupport) -> None:
    with pytest.raises(ValidationError):
        evidence(support=support, source_ids=())


def test_unknown_cannot_claim_verification_mode() -> None:
    with pytest.raises(ValidationError):
        evidence(support=BrokerCapabilitySupport.UNKNOWN)
    assert evidence(support=BrokerCapabilitySupport.UNKNOWN, source_ids=(), modes=()).verification_modes == ()


def test_matrix_normalizes_broker_rejects_duplicates_and_orders_entries() -> None:
    matrix = BrokerCapabilityMatrix(
        broker=" sinopac ",
        entries=(evidence(BrokerCapability.ORDER_PLACE), evidence(BrokerCapability.ACCOUNT_QUERY)),
    )
    assert matrix.broker == "SINOPAC"
    assert [entry.capability for entry in matrix.entries] == [
        BrokerCapability.ACCOUNT_QUERY, BrokerCapability.ORDER_PLACE,
    ]
    with pytest.raises(ValidationError):
        BrokerCapabilityMatrix(broker="SINOPAC", entries=(evidence(), evidence()))
    with pytest.raises(ValidationError):
        BrokerCapabilityMatrix(broker=" ", entries=())


def test_matrix_is_immutable_and_extra_forbid() -> None:
    matrix = BrokerCapabilityMatrix(broker="SINOPAC", entries=(evidence(),))
    with pytest.raises(ValidationError):
        matrix.broker = "OTHER"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        BrokerCapabilityMatrix(broker="SINOPAC", entries=(), unexpected=True)


def test_get_known_and_missing_capability() -> None:
    matrix = BrokerCapabilityMatrix(broker="SINOPAC", entries=(evidence(),))
    assert get_broker_capability(matrix, BrokerCapability.ACCOUNT_QUERY) is matrix.entries[0]
    assert get_broker_capability(matrix, BrokerCapability.ORDER_PLACE) is None


def test_require_supported_and_required_mode() -> None:
    matrix = BrokerCapabilityMatrix(broker="SINOPAC", entries=(evidence(),))
    assert require_broker_capability(matrix, BrokerCapability.ACCOUNT_QUERY) is matrix.entries[0]
    assert require_broker_capability(
        matrix, BrokerCapability.ACCOUNT_QUERY,
        required_mode=BrokerVerificationMode.DOCUMENTATION,
    ) is matrix.entries[0]


@pytest.mark.parametrize(
    ("entries", "capability"),
    [
        ((), BrokerCapability.ACCOUNT_QUERY),
        ((evidence(support=BrokerCapabilitySupport.UNSUPPORTED),), BrokerCapability.ACCOUNT_QUERY),
        ((evidence(support=BrokerCapabilitySupport.UNKNOWN, source_ids=(), modes=()),), BrokerCapability.ACCOUNT_QUERY),
    ],
)
def test_require_rejects_missing_unsupported_or_unknown(entries, capability) -> None:
    matrix = BrokerCapabilityMatrix(broker="SINOPAC", entries=entries)
    with pytest.raises(BrokerCapabilityUnavailableError):
        require_broker_capability(matrix, capability)


def test_verification_modes_do_not_imply_each_other() -> None:
    documentation = BrokerCapabilityMatrix(broker="SINOPAC", entries=(evidence(),))
    with pytest.raises(BrokerCapabilityUnavailableError):
        require_broker_capability(
            documentation, BrokerCapability.ACCOUNT_QUERY,
            required_mode=BrokerVerificationMode.SIMULATION,
        )
    simulation = BrokerCapabilityMatrix(
        broker="SINOPAC",
        entries=(evidence(modes=(BrokerVerificationMode.SIMULATION,)),),
    )
    with pytest.raises(BrokerCapabilityUnavailableError):
        require_broker_capability(
            simulation, BrokerCapability.ACCOUNT_QUERY,
            required_mode=BrokerVerificationMode.PRODUCTION,
        )


def test_sinopac_matrix_has_exact_documentation_evidence() -> None:
    matrix = SINOPAC_CAPABILITY_MATRIX
    assert matrix.broker == "SINOPAC"
    assert len(matrix.entries) == 8
    assert {entry.capability for entry in matrix.entries} == set(BrokerCapability)
    assert all(entry.sdk_version == "1.7.6" for entry in matrix.entries)
    assert all(entry.verified_on == date(2026, 9, 25) for entry in matrix.entries)
    assert all(entry.support is BrokerCapabilitySupport.SUPPORTED for entry in matrix.entries)
    assert all(
        entry.verification_modes == (BrokerVerificationMode.DOCUMENTATION,)
        for entry in matrix.entries
    )


def test_sinopac_matrix_source_mapping_is_exact() -> None:
    expected = {
        BrokerCapability.ACCOUNT_QUERY: ("SRC-SINOPAC-LOGIN-001",),
        BrokerCapability.POSITION_QUERY: ("SRC-SINOPAC-POSITION-001",),
        BrokerCapability.ORDER_PLACE: ("SRC-SINOPAC-FUT-ORDER-001",),
        BrokerCapability.ORDER_UPDATE: ("SRC-SINOPAC-FUT-ORDER-001",),
        BrokerCapability.ORDER_CANCEL: ("SRC-SINOPAC-FUT-ORDER-001",),
        BrokerCapability.ORDER_STATUS: ("SRC-SINOPAC-ORDER-STATUS-001",),
        BrokerCapability.TRADE_LIST: ("SRC-SINOPAC-ORDER-STATUS-001",),
        BrokerCapability.ORDER_DEAL_EVENT: (
            "SRC-SINOPAC-ORDER-EVENT-001", "SRC-SINOPAC-RELEASE-001",
        ),
    }
    assert {entry.capability: entry.source_ids for entry in SINOPAC_CAPABILITY_MATRIX.entries} == expected


def test_capability_contract_has_no_broker_action_surface() -> None:
    forbidden = {"login", "logout", "activate_ca", "submit_order", "cancel_order"}
    assert forbidden.isdisjoint(dir(BrokerCapabilityMatrix))
    assert forbidden.isdisjoint(dir(BrokerCapabilityEvidence))
