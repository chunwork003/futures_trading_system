from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from trading.account import (
    AccountPosition,
    BrokerAccount,
    BrokerPositionProvider,
    BrokerPositionSnapshot,
    PositionDirection,
)
from trading.reconciliation import (
    ExternalStateUnknownError,
    ExpectedPositionLoader,
    PositionComparisonError,
    ReconciliationCase,
    ReconciliationCaseError,
    ReconciliationCaseState,
    ReconciliationCollectionError,
    ReconciliationPolicy,
    ReconciliationResult,
    ReconciliationStatus,
    StartupReadinessState,
    StartupReconciliationResult,
    compare_positions,
    create_reconciliation_case,
    reconcile_position_collections,
    reconcile_startup,
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


def _account() -> BrokerAccount:
    return BrokerAccount(
        broker="SINOPAC",
        account_ref="9A95-1234567",
        account_type="FUTURES_OPTIONS",
    )


class _ExpectedLoader:
    def __init__(self, positions: tuple[AccountPosition, ...]) -> None:
        self.positions = positions
        self.accounts: list[BrokerAccount] = []

    def load_positions(
        self,
        account: BrokerAccount,
    ) -> tuple[AccountPosition, ...]:
        self.accounts.append(account)
        return self.positions


class _PositionProvider:
    def __init__(self, positions: tuple[BrokerPositionSnapshot, ...]) -> None:
        self.positions = positions
        self.accounts: list[BrokerAccount] = []

    def list_positions(
        self,
        account: BrokerAccount,
    ) -> tuple[BrokerPositionSnapshot, ...]:
        self.accounts.append(account)
        return self.positions


def test_collection_error_and_loader_protocol_are_explicit() -> None:
    assert issubclass(ReconciliationCollectionError, ValueError)
    assert isinstance(_ExpectedLoader(()), ExpectedPositionLoader)
    assert isinstance(_PositionProvider(()), BrokerPositionProvider)


@pytest.mark.parametrize("side", ["expected", "actual"])
def test_duplicate_exact_position_key_is_rejected(side: str) -> None:
    expected = (_expected(), _expected()) if side == "expected" else ()
    actual = (_actual(), _actual()) if side == "actual" else ()

    with pytest.raises(ReconciliationCollectionError, match=f"duplicate {side}"):
        reconcile_position_collections(
            expected_positions=expected,
            actual_positions=actual,
        )


def test_exact_expected_only_and_actual_only_collection_results() -> None:
    expected = _expected(contract_id=101)
    actual = _actual(contract_id=101, quantity=3)
    expected_only = _expected(instrument_id=2, contract_id=102)
    actual_only = _actual(instrument_id=3, contract_id=103)

    results = reconcile_position_collections(
        expected_positions=(expected_only, expected),
        actual_positions=(actual_only, actual),
    )

    assert [result.status for result in results] == [
        ReconciliationStatus.QUANTITY_MISMATCH,
        ReconciliationStatus.INTERNAL_ONLY,
        ReconciliationStatus.BROKER_ONLY,
    ]
    assert results[0].expected is expected
    assert results[0].actual is actual


def test_unique_unmatched_pair_is_contract_mismatch() -> None:
    result = reconcile_position_collections(
        expected_positions=(_expected(contract_id=101),),
        actual_positions=(_actual(contract_id=102),),
    )

    assert len(result) == 1
    assert result[0].status == ReconciliationStatus.CONTRACT_MISMATCH


def test_ambiguous_unmatched_collection_never_guesses_by_order_quantity_or_direction() -> None:
    expected = (
        _expected(contract_id=101, quantity=1),
        _expected(
            contract_id=102,
            quantity=2,
            direction=PositionDirection.SHORT,
        ),
    )
    actual = (
        _actual(
            contract_id=201,
            quantity=2,
            direction=PositionDirection.SHORT,
        ),
        _actual(contract_id=202, quantity=1),
    )

    with pytest.raises(ReconciliationCollectionError, match="ambiguous"):
        reconcile_position_collections(
            expected_positions=expected,
            actual_positions=actual,
        )
    with pytest.raises(ReconciliationCollectionError, match="ambiguous"):
        reconcile_position_collections(
            expected_positions=tuple(reversed(expected)),
            actual_positions=tuple(reversed(actual)),
        )


def test_collection_output_is_deterministic_across_permutations_and_scopes() -> None:
    expected = (
        _expected(broker="ZBROKER", account_ref="B", instrument_id=2, contract_id=3),
        _expected(contract_id=2),
        _expected(contract_id=None),
    )
    actual = (
        _actual(contract_id=2),
        _actual(contract_id=None),
        _actual(broker="ZBROKER", account_ref="B", instrument_id=2, contract_id=3),
    )

    forward = reconcile_position_collections(
        expected_positions=expected,
        actual_positions=actual,
    )
    reversed_result = reconcile_position_collections(
        expected_positions=tuple(reversed(expected)),
        actual_positions=tuple(reversed(actual)),
    )

    assert forward == reversed_result
    assert [result.expected.contract_id for result in forward] == [None, 2, 3]


def test_collection_reconciliation_does_not_mutate_inputs() -> None:
    expected = (_expected(),)
    actual = (_actual(),)
    expected_before = tuple(item.model_dump() for item in expected)
    actual_before = tuple(item.model_dump() for item in actual)

    reconcile_position_collections(
        expected_positions=expected,
        actual_positions=actual,
    )

    assert tuple(item.model_dump() for item in expected) == expected_before
    assert tuple(item.model_dump() for item in actual) == actual_before


def test_startup_readiness_state_has_exact_values() -> None:
    assert [state.value for state in StartupReadinessState] == [
        "READY",
        "HALT",
        "REVIEW",
    ]


def test_startup_result_is_immutable_extra_forbid_and_ready_is_clean_only() -> None:
    result = StartupReconciliationResult(
        policy=ReconciliationPolicy.STRICT_HALT,
        state=StartupReadinessState.READY,
        results=(),
        strategy_state_ready=True,
    )
    with pytest.raises(ValidationError):
        result.state = StartupReadinessState.HALT
    with pytest.raises(ValidationError, match="unexpected"):
        StartupReconciliationResult(
            **result.model_dump(),
            unexpected=True,
        )
    with pytest.raises(ValidationError, match="strategy_state_ready"):
        StartupReconciliationResult(
            policy=ReconciliationPolicy.STRICT_HALT,
            state=StartupReadinessState.READY,
            results=(),
            strategy_state_ready=False,
        )
    with pytest.raises(ValidationError, match="all reconciliation"):
        StartupReconciliationResult(
            policy=ReconciliationPolicy.STRICT_HALT,
            state=StartupReadinessState.READY,
            results=(_mismatch_result(),),
            strategy_state_ready=True,
        )


def _startup(
    *,
    expected: tuple[AccountPosition, ...] = (),
    actual: tuple[BrokerPositionSnapshot, ...] = (),
    policy: ReconciliationPolicy = ReconciliationPolicy.STRICT_HALT,
    strategy_state_ready: bool = True,
) -> tuple[StartupReconciliationResult, _ExpectedLoader, _PositionProvider]:
    loader = _ExpectedLoader(expected)
    provider = _PositionProvider(actual)
    result = reconcile_startup(
        account=_account(),
        expected_loader=loader,
        broker_position_provider=provider,
        policy=policy,
        strategy_state_ready=strategy_state_ready,
    )
    return result, loader, provider


def test_clean_empty_and_matched_startup_are_ready() -> None:
    empty, _, _ = _startup()
    matched, _, _ = _startup(expected=(_expected(),), actual=(_actual(),))

    assert empty.state == StartupReadinessState.READY
    assert empty.results == ()
    assert matched.state == StartupReadinessState.READY
    assert matched.results[0].status == ReconciliationStatus.MATCH


def test_strategy_state_not_ready_has_halt_precedence() -> None:
    result, _, _ = _startup(
        expected=(_expected(),),
        actual=(),
        policy=ReconciliationPolicy.MANUAL_REVIEW,
        strategy_state_ready=False,
    )

    assert result.state == StartupReadinessState.HALT


@pytest.mark.parametrize(
    ("policy", "state"),
    [
        (ReconciliationPolicy.STRICT_HALT, StartupReadinessState.HALT),
        (ReconciliationPolicy.MANUAL_REVIEW, StartupReadinessState.REVIEW),
        (ReconciliationPolicy.BROKER_AUTHORITATIVE, StartupReadinessState.REVIEW),
        (ReconciliationPolicy.INTERNAL_AUTHORITATIVE, StartupReadinessState.REVIEW),
    ],
)
def test_mismatch_startup_policy_mapping(
    policy: ReconciliationPolicy,
    state: StartupReadinessState,
) -> None:
    result, _, _ = _startup(expected=(_expected(),), policy=policy)

    assert result.state == state
    assert result.results[0].status == ReconciliationStatus.INTERNAL_ONLY


class _UnknownProvider:
    def __init__(self, message: str) -> None:
        self.message = message

    def list_positions(
        self,
        account: BrokerAccount,
    ) -> tuple[BrokerPositionSnapshot, ...]:
        raise ExternalStateUnknownError(self.message)


@pytest.mark.parametrize(
    ("policy", "state"),
    [
        (ReconciliationPolicy.STRICT_HALT, StartupReadinessState.HALT),
        (ReconciliationPolicy.MANUAL_REVIEW, StartupReadinessState.REVIEW),
        (ReconciliationPolicy.BROKER_AUTHORITATIVE, StartupReadinessState.REVIEW),
        (ReconciliationPolicy.INTERNAL_AUTHORITATIVE, StartupReadinessState.REVIEW),
    ],
)
def test_external_unknown_conversion_and_policy_mapping(
    policy: ReconciliationPolicy,
    state: StartupReadinessState,
) -> None:
    result = reconcile_startup(
        account=_account(),
        expected_loader=_ExpectedLoader((_expected(),)),
        broker_position_provider=_UnknownProvider(" broker unavailable "),
        policy=policy,
        strategy_state_ready=True,
    )

    assert result.state == state
    assert result.results[0].status == ReconciliationStatus.UNKNOWN_EXTERNAL_STATE
    assert result.results[0].actual is None
    assert result.results[0].evidence == ("broker unavailable",)


def test_blank_external_unknown_uses_deterministic_evidence_and_strategy_halt() -> None:
    result = reconcile_startup(
        account=_account(),
        expected_loader=_ExpectedLoader(()),
        broker_position_provider=_UnknownProvider("  "),
        policy=ReconciliationPolicy.MANUAL_REVIEW,
        strategy_state_ready=False,
    )

    assert result.state == StartupReadinessState.HALT
    assert result.results[0].evidence == ("broker external state unavailable",)


def test_unexpected_provider_and_loader_errors_propagate() -> None:
    class BrokenLoader:
        def load_positions(self, account: BrokerAccount) -> tuple[AccountPosition, ...]:
            raise LookupError("loader failed")

    class BrokenProvider:
        def list_positions(
            self,
            account: BrokerAccount,
        ) -> tuple[BrokerPositionSnapshot, ...]:
            raise RuntimeError("programming failure")

    with pytest.raises(LookupError, match="loader failed"):
        reconcile_startup(
            account=_account(),
            expected_loader=BrokenLoader(),
            broker_position_provider=_PositionProvider(()),
            policy=ReconciliationPolicy.STRICT_HALT,
            strategy_state_ready=True,
        )
    with pytest.raises(RuntimeError, match="programming failure"):
        reconcile_startup(
            account=_account(),
            expected_loader=_ExpectedLoader(()),
            broker_position_provider=BrokenProvider(),
            policy=ReconciliationPolicy.STRICT_HALT,
            strategy_state_ready=True,
        )


@pytest.mark.parametrize("source", ["loader", "provider"])
def test_wrong_account_output_is_rejected(source: str) -> None:
    wrong_expected = (_expected(account_ref="OTHER"),) if source == "loader" else ()
    wrong_actual = (_actual(account_ref="OTHER"),) if source == "provider" else ()

    with pytest.raises(ReconciliationCollectionError, match="account scope"):
        _startup(expected=wrong_expected, actual=wrong_actual)


def test_loader_and_provider_receive_supplied_account() -> None:
    account = _account()
    loader = _ExpectedLoader(())
    provider = _PositionProvider(())

    reconcile_startup(
        account=account,
        expected_loader=loader,
        broker_position_provider=provider,
        policy=ReconciliationPolicy.STRICT_HALT,
        strategy_state_ready=True,
    )

    assert loader.accounts == [account]
    assert provider.accounts == [account]


def test_startup_contract_exposes_no_corrective_capability() -> None:
    for model in (StartupReconciliationResult,):
        for forbidden in ("submit", "repair", "overwrite", "adopt"):
            assert forbidden not in model.__dict__
