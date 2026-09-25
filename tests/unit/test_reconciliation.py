from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from trading.account import (
    AccountPosition,
    BrokerPositionSnapshot,
    PositionDirection,
)
from trading.reconciliation import (
    ExternalStateUnknownError,
    PositionComparisonError,
    ReconciliationCase,
    ReconciliationCaseError,
    ReconciliationCaseState,
    ReconciliationPolicy,
    ReconciliationResult,
    ReconciliationStatus,
    compare_positions,
    create_reconciliation_case,
    resolve_reconciliation_case,
)


def _expected(**overrides: object) -> AccountPosition:
    values: dict[str, object] = {
        "broker": "SINOPAC",
        "account_ref": "9A95-1234567",
        "instrument_id": 1,
        "contract_id": 101,
        "direction": PositionDirection.LONG,
        "quantity": 2,
    }
    values.update(overrides)
    return AccountPosition(**values)


def _actual(**overrides: object) -> BrokerPositionSnapshot:
    values: dict[str, object] = {
        **_expected().model_dump(),
        "observed_at": datetime.now(timezone.utc),
    }
    values.update(overrides)
    return BrokerPositionSnapshot(**values)


@pytest.mark.parametrize(
    ("expected", "actual", "status"),
    [
        (None, None, ReconciliationStatus.MATCH),
        (_expected(), None, ReconciliationStatus.INTERNAL_ONLY),
        (None, _actual(), ReconciliationStatus.BROKER_ONLY),
        (_expected(), _actual(), ReconciliationStatus.MATCH),
        (
            _expected(),
            _actual(contract_id=102),
            ReconciliationStatus.CONTRACT_MISMATCH,
        ),
        (
            _expected(),
            _actual(direction=PositionDirection.SHORT),
            ReconciliationStatus.DIRECTION_MISMATCH,
        ),
        (
            _expected(),
            _actual(quantity=3),
            ReconciliationStatus.QUANTITY_MISMATCH,
        ),
    ],
)
def test_pairwise_reconciliation_statuses(
    expected: AccountPosition | None,
    actual: BrokerPositionSnapshot | None,
    status: ReconciliationStatus,
) -> None:
    result = compare_positions(expected, actual)

    assert result.status == status
    assert result.expected is expected
    assert result.actual is actual


@pytest.mark.parametrize(
    "actual",
    [
        _actual(broker="OTHER"),
        _actual(account_ref="OTHER-ACCOUNT"),
        _actual(instrument_id=2),
    ],
)
def test_non_comparable_identity_is_explicit(
    actual: BrokerPositionSnapshot,
) -> None:
    with pytest.raises(PositionComparisonError, match="do not share"):
        compare_positions(_expected(), actual)


def test_comparison_does_not_mutate_or_offer_corrective_execution() -> None:
    expected = _expected()
    actual = _actual(quantity=3)
    before_expected = expected.model_dump()
    before_actual = actual.model_dump()

    result = compare_positions(expected, actual)

    assert expected.model_dump() == before_expected
    assert actual.model_dump() == before_actual
    assert "submit" not in result.__class__.__dict__
    assert "repair" not in result.__class__.__dict__


def _mismatch_result() -> ReconciliationResult:
    return compare_positions(_expected(), _actual(quantity=3))


def _unknown_result() -> ReconciliationResult:
    return ReconciliationResult(
        status=ReconciliationStatus.UNKNOWN_EXTERNAL_STATE,
        expected=_expected(),
        actual=None,
        evidence=(" broker observation unavailable ",),
    )


def test_reconciliation_status_has_exact_values() -> None:
    assert [status.value for status in ReconciliationStatus] == [
        "MATCH",
        "INTERNAL_ONLY",
        "BROKER_ONLY",
        "CONTRACT_MISMATCH",
        "DIRECTION_MISMATCH",
        "QUANTITY_MISMATCH",
        "UNKNOWN_EXTERNAL_STATE",
    ]


def test_comparison_precedence_remains_contract_direction_quantity() -> None:
    expected = _expected()

    assert compare_positions(
        expected,
        _actual(
            contract_id=102,
            direction=PositionDirection.SHORT,
            quantity=3,
        ),
    ).status == ReconciliationStatus.CONTRACT_MISMATCH
    assert compare_positions(
        expected,
        _actual(direction=PositionDirection.SHORT, quantity=3),
    ).status == ReconciliationStatus.DIRECTION_MISMATCH


def test_result_evidence_defaults_to_empty_tuple_and_normalizes() -> None:
    default_result = _mismatch_result()
    result = ReconciliationResult(
        status=default_result.status,
        expected=default_result.expected,
        actual=default_result.actual,
        evidence=[" broker quantity differs ", " review required "],
    )

    assert default_result.evidence == ()
    assert result.evidence == (
        "broker quantity differs",
        "review required",
    )


def test_blank_evidence_is_rejected() -> None:
    with pytest.raises(ValidationError, match="must not be blank"):
        ReconciliationResult(
            status=ReconciliationStatus.INTERNAL_ONLY,
            expected=_expected(),
            actual=None,
            evidence=("  ",),
        )


def test_unknown_external_state_requires_evidence_and_no_actual() -> None:
    with pytest.raises(ValidationError, match="requires evidence"):
        ReconciliationResult(
            status=ReconciliationStatus.UNKNOWN_EXTERNAL_STATE,
            expected=_expected(),
            actual=None,
        )
    with pytest.raises(ValidationError, match="actual must be None"):
        ReconciliationResult(
            status=ReconciliationStatus.UNKNOWN_EXTERNAL_STATE,
            expected=_expected(),
            actual=_actual(),
            evidence=("observation failed",),
        )


def test_external_state_unknown_error_is_runtime_error_contract() -> None:
    assert issubclass(ExternalStateUnknownError, RuntimeError)


def test_policy_and_case_state_have_exact_values() -> None:
    assert [policy.value for policy in ReconciliationPolicy] == [
        "STRICT_HALT",
        "MANUAL_REVIEW",
        "BROKER_AUTHORITATIVE",
        "INTERNAL_AUTHORITATIVE",
    ]
    assert [state.value for state in ReconciliationCaseState] == [
        "HALT",
        "REVIEW_REQUIRED",
        "RESOLVED",
    ]


def test_case_id_is_normalized_and_match_cannot_create_case() -> None:
    case = create_reconciliation_case(
        case_id=" CASE-001 ",
        result=_mismatch_result(),
        policy=ReconciliationPolicy.STRICT_HALT,
    )
    assert case.case_id == "CASE-001"

    with pytest.raises(ReconciliationCaseError, match="MATCH"):
        create_reconciliation_case(
            case_id="CASE-002",
            result=compare_positions(None, None),
            policy=ReconciliationPolicy.STRICT_HALT,
        )
    with pytest.raises(ValidationError, match="case_id must not be blank"):
        create_reconciliation_case(
            case_id="  ",
            result=_mismatch_result(),
            policy=ReconciliationPolicy.STRICT_HALT,
        )


@pytest.mark.parametrize(
    ("policy", "state"),
    [
        (ReconciliationPolicy.STRICT_HALT, ReconciliationCaseState.HALT),
        (
            ReconciliationPolicy.MANUAL_REVIEW,
            ReconciliationCaseState.REVIEW_REQUIRED,
        ),
        (
            ReconciliationPolicy.BROKER_AUTHORITATIVE,
            ReconciliationCaseState.REVIEW_REQUIRED,
        ),
        (
            ReconciliationPolicy.INTERNAL_AUTHORITATIVE,
            ReconciliationCaseState.REVIEW_REQUIRED,
        ),
    ],
)
def test_mismatch_policy_mapping(
    policy: ReconciliationPolicy,
    state: ReconciliationCaseState,
) -> None:
    case = create_reconciliation_case(
        case_id="CASE-001",
        result=_mismatch_result(),
        policy=policy,
    )

    assert case.state == state
    assert case.resolution_note is None


@pytest.mark.parametrize(
    ("policy", "state"),
    [
        (ReconciliationPolicy.STRICT_HALT, ReconciliationCaseState.HALT),
        (
            ReconciliationPolicy.MANUAL_REVIEW,
            ReconciliationCaseState.REVIEW_REQUIRED,
        ),
        (
            ReconciliationPolicy.BROKER_AUTHORITATIVE,
            ReconciliationCaseState.REVIEW_REQUIRED,
        ),
        (
            ReconciliationPolicy.INTERNAL_AUTHORITATIVE,
            ReconciliationCaseState.REVIEW_REQUIRED,
        ),
    ],
)
def test_unknown_external_state_uses_same_policy_mapping(
    policy: ReconciliationPolicy,
    state: ReconciliationCaseState,
) -> None:
    case = create_reconciliation_case(
        case_id="CASE-UNKNOWN",
        result=_unknown_result(),
        policy=policy,
    )

    assert case.state == state


@pytest.mark.parametrize(
    "policy",
    [
        ReconciliationPolicy.STRICT_HALT,
        ReconciliationPolicy.MANUAL_REVIEW,
    ],
)
def test_halt_and_review_cases_resolve_without_mutating_original(
    policy: ReconciliationPolicy,
) -> None:
    original = create_reconciliation_case(
        case_id="CASE-001",
        result=_mismatch_result(),
        policy=policy,
    )

    resolved = resolve_reconciliation_case(
        original,
        resolution_note=" reviewed and accepted ",
    )

    assert resolved.state == ReconciliationCaseState.RESOLVED
    assert resolved.resolution_note == "reviewed and accepted"
    assert original.state != ReconciliationCaseState.RESOLVED
    assert original.resolution_note is None


def test_invalid_case_resolution_is_explicit() -> None:
    case = create_reconciliation_case(
        case_id="CASE-001",
        result=_mismatch_result(),
        policy=ReconciliationPolicy.STRICT_HALT,
    )
    with pytest.raises(ReconciliationCaseError, match="must not be blank"):
        resolve_reconciliation_case(case, resolution_note="  ")

    resolved = resolve_reconciliation_case(case, resolution_note="done")
    with pytest.raises(ReconciliationCaseError, match="again"):
        resolve_reconciliation_case(resolved, resolution_note="again")


def test_case_state_and_resolution_note_invariants() -> None:
    common = {
        "case_id": "CASE-001",
        "result": _mismatch_result(),
        "policy": ReconciliationPolicy.MANUAL_REVIEW,
    }
    with pytest.raises(ValidationError, match="must not have"):
        ReconciliationCase(
            **common,
            state=ReconciliationCaseState.REVIEW_REQUIRED,
            resolution_note="premature",
        )
    with pytest.raises(ValidationError, match="requires resolution_note"):
        ReconciliationCase(
            **common,
            state=ReconciliationCaseState.RESOLVED,
        )


def test_reconciliation_models_are_immutable_extra_forbid_and_non_corrective() -> None:
    result = _mismatch_result()
    case = create_reconciliation_case(
        case_id="CASE-001",
        result=result,
        policy=ReconciliationPolicy.BROKER_AUTHORITATIVE,
    )

    with pytest.raises(ValidationError):
        result.status = ReconciliationStatus.MATCH
    with pytest.raises(ValidationError):
        case.state = ReconciliationCaseState.RESOLVED
    with pytest.raises(ValidationError, match="unexpected"):
        ReconciliationResult(
            status=ReconciliationStatus.INTERNAL_ONLY,
            expected=_expected(),
            actual=None,
            unexpected=True,
        )
    with pytest.raises(ValidationError, match="unexpected"):
        ReconciliationCase(
            case_id="CASE-001",
            result=result,
            policy=ReconciliationPolicy.MANUAL_REVIEW,
            state=ReconciliationCaseState.REVIEW_REQUIRED,
            unexpected=True,
        )
    for forbidden in ("submit", "cancel", "repair", "overwrite"):
        assert forbidden not in ReconciliationCase.__dict__
        assert forbidden not in ReconciliationResult.__dict__
