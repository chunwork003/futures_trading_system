
from datetime import datetime, timezone

import pytest

from persistence.account_authority import AccountAuthorityCommitReceipt, AccountRecoveryCheckpoint, AccountStateHead

from persistence.reconciliation import (
    ReconciliationCaseVersion,
)
from persistence.recovery import (
    ExecutionRestoreResult,
    ExecutionRestoreStatus,
    RecoveryCut,
    RecoveryReadinessState,
    recover_runtime,
)
from persistence.strategy_state import (
    StrategyStateSnapshot,
)
from strategy.instance import (
    CanonicalInstrumentBindingProvenance,
    StrategyInstance,
    config_fingerprint,
)
from strategy.registry import StrategyRegistry
from strategies.ema_cross import (
    EMACrossStrategy,
)
from trading.account import (
    AccountPosition,
    BrokerAccount,
    PositionDirection,
)
from trading.reconciliation import (
    ReconciliationPolicy,
    compare_positions,
    create_reconciliation_case,
)


NOW = datetime(
    2026,
    9,
    25,
    1,
    tzinfo=timezone.utc,
)

ACCOUNT = BrokerAccount(
    broker="SINOPAC",
    account_ref="A",
)

MOR1_A = "mor1_" + ("a" * 64)
MOR1_B = "mor1_" + ("b" * 64)


class ExecutionLoader:
    def __init__(self, trace):
        self.trace = trace

    def load(self, account):
        self.trace.append(
            "execution"
        )
        head=AccountStateHead(broker=account.broker,account_ref=account.account_ref,current_revision=1,initialized=True)
        checkpoint=AccountRecoveryCheckpoint(broker=account.broker,account_ref=account.account_ref,account_revision=1,expected_snapshot_id="S1",authority_commit_id="AC1",recorded_at=NOW)
        receipt=AccountAuthorityCommitReceipt(authority_commit_id="AC1",mutation_fingerprint="FP",broker=account.broker,account_ref=account.account_ref,committed_revision=1,expected_snapshot_id="S1",recorded_at=NOW)
        return ExecutionRestoreResult(status=ExecutionRestoreStatus.VALID,cut=RecoveryCut(account=account,head=head,checkpoint=checkpoint,receipt=receipt,inbox_count=0,application_count=0),evidence=("test coherent cut",))


class ExpectedLoader:
    def __init__(
        self,
        positions,
        trace,
    ):
        self.positions = positions
        self.trace = trace

    def load_positions(
        self,
        account,
    ):
        self.trace.append(
            "expected"
        )

        return self.positions


class Provider:
    def __init__(
        self,
        positions,
        trace,
    ):
        self.positions = positions
        self.trace = trace

    def list_positions(
        self,
        account,
    ):
        self.trace.append(
            "broker"
        )

        return self.positions


class Cases:
    def __init__(
        self,
        values=(),
    ):
        self.values = values

    def unresolved(self, account):
        return self.values


class Instances:
    def __init__(
        self,
        value,
        trace,
    ):
        self.value = value
        self.trace = trace

    def get(
        self,
        key,
    ):
        self.trace.append(
            "instance"
        )

        return self.value


class States:
    def __init__(
        self,
        value,
        trace,
    ):
        self.value = value
        self.trace = trace

    def latest(
        self,
        key,
    ):
        self.trace.append(
            "state"
        )

        return self.value


def setup(
    revision_id=MOR1_A,
):
    config = {
        "symbol": "TX",
        "timeframe": "1m",
    }

    item = StrategyInstance(
        strategy_instance_id="SI",
        strategy_id="EMA_CROSS",
        strategy_version="1.0.0",
        config_version="C1",
        config_fingerprint=(
            config_fingerprint(
                config
            )
        ),
        instrument_id=1,
        timeframe="1m",
        config_json=config,
        instrument_binding_provenance=(
            CanonicalInstrumentBindingProvenance(
                instrument_id=1,
                authority_id="CANONICAL-INSTRUMENT-PROVISIONING",
                authority_version="V1",
                reference_id="BIND-SI",
            )
        ),
    )

    snapshot = (
        StrategyStateSnapshot(
            snapshot_id="SS",
            strategy_instance_id="SI",
            strategy_id="EMA_CROSS",
            strategy_version="1.0.0",
            config_version="C1",
            config_fingerprint=(
                item.config_fingerprint
            ),
            instrument_id=1,
            timeframe="1m",
            state_schema_version=1,
            last_market_observation_revision_id=(
                revision_id
            ),
            captured_at=NOW,
            state_json={
                "schema_version": 1,
                "previous_ema20": 1.0,
                "previous_ema60": 2.0,
            },
        )
    )

    registry = StrategyRegistry()

    registry.register(
        "EMA_CROSS",
        "1.0.0",
        EMACrossStrategy,
    )

    return (
        item,
        snapshot,
        registry,
    )


def recover(
    *,
    expected=(),
    actual=(),
    cases=(),
    snapshot_override=True,
    snapshot_revision=MOR1_A,
    required_revision=MOR1_A,
    legacy_required=None,
    instance_transform=None,
    transition_authority=None,
    use_transition_repository=False,
):
    trace = []

    transition_repository = None
    if use_transition_repository:
        class _Transitions:
            def current(self, key):
                trace.append("transition")
                return transition_authority

        transition_repository = _Transitions()

    (
        item,
        snapshot,
        registry,
    ) = setup(
        snapshot_revision
    )

    if instance_transform is not None:
        item = instance_transform(item)

    snapshot_value = (
        snapshot
        if snapshot_override is True
        else snapshot_override
    )

    result = recover_runtime(
        account=ACCOUNT,
        execution_loader=(
            ExecutionLoader(
                trace
            )
        ),
        expected_loader=(
            ExpectedLoader(
                expected,
                trace,
            )
        ),
        broker_position_provider=(
            Provider(
                actual,
                trace,
            )
        ),
        reconciliation_policy=(
            ReconciliationPolicy
            .STRICT_HALT
        ),
        case_repository=Cases(
            cases
        ),
        strategy_instance_ids=(
            "SI",
        ),
        instance_repository=(
            Instances(
                item,
                trace,
            )
        ),
        state_repository=(
            States(
                snapshot_value,
                trace,
            )
        ),
        registry=registry,
        transition_repository=transition_repository,
        required_market_observation_revision_id=(
            required_revision
        ),
        required_market_observation_id=(
            legacy_required
        ),
    )

    return (
        result,
        trace,
    )


def test_legacy_recovery_restores_strategy_but_cannot_claim_account_ready():
    result, trace = recover()

    assert (
        result.state
        is RecoveryReadinessState.REVIEW
    )

    assert isinstance(
        result.restored_strategies[0],
        EMACrossStrategy,
    )

    assert trace == [
        "execution",
        "expected",
        "broker",
        "instance",
        "state",
    ]


def test_account_halt_prevents_strategy_restore():
    expected = (
        AccountPosition(
            broker="SINOPAC",
            account_ref="A",
            instrument_id=1,
            contract_id=2,
            direction=(
                PositionDirection.LONG
            ),
            quantity=1,
        ),
    )

    result, trace = recover(
        expected=expected
    )

    assert (
        result.state
        is RecoveryReadinessState.HALT
    )

    assert "instance" not in trace
    assert "state" not in trace


def test_account_review_prevents_ready_and_restore():
    trace = []

    expected = (
        AccountPosition(
            broker="SINOPAC",
            account_ref="A",
            instrument_id=1,
            contract_id=2,
            direction=(
                PositionDirection.LONG
            ),
            quantity=1,
        ),
    )

    (
        item,
        snapshot,
        registry,
    ) = setup()

    result = recover_runtime(
        account=ACCOUNT,
        execution_loader=(
            ExecutionLoader(
                trace
            )
        ),
        expected_loader=(
            ExpectedLoader(
                expected,
                trace,
            )
        ),
        broker_position_provider=(
            Provider(
                (),
                trace,
            )
        ),
        reconciliation_policy=(
            ReconciliationPolicy
            .MANUAL_REVIEW
        ),
        case_repository=Cases(),
        strategy_instance_ids=(
            "SI",
        ),
        instance_repository=(
            Instances(
                item,
                trace,
            )
        ),
        state_repository=(
            States(
                snapshot,
                trace,
            )
        ),
        registry=registry,
        required_market_observation_revision_id=(
            MOR1_A
        ),
    )

    assert (
        result.state
        is RecoveryReadinessState.REVIEW
    )

    assert "instance" not in trace


def test_unresolved_case_gate_precedes_strategy_restore():
    mismatch = compare_positions(
        AccountPosition(
            broker="SINOPAC",
            account_ref="A",
            instrument_id=1,
            contract_id=2,
            direction=(
                PositionDirection.LONG
            ),
            quantity=1,
        ),
        None,
    )

    case = create_reconciliation_case(
        case_id="CASE",
        result=mismatch,
        policy=(
            ReconciliationPolicy
            .STRICT_HALT
        ),
    )

    version = (
        ReconciliationCaseVersion(
            case_id="CASE",
            version=1,
            recorded_at=NOW,
            reconciliation_case=case,
        )
    )

    result, trace = recover(
        cases=(
            version,
        )
    )

    assert (
        result.state
        is RecoveryReadinessState.HALT
    )

    assert "instance" not in trace


@pytest.mark.parametrize(
    "snapshot_override,snapshot_revision",
    [
        (
            None,
            MOR1_A,
        ),
        (
            True,
            MOR1_B,
        ),
    ],
)
def test_missing_snapshot_or_revision_boundary_mismatch_halts(
    snapshot_override,
    snapshot_revision,
):
    result, _ = recover(
        snapshot_override=(
            snapshot_override
        ),
        snapshot_revision=(
            snapshot_revision
        ),
    )

    assert (
        result.state
        is RecoveryReadinessState.HALT
    )


@pytest.mark.parametrize(
    "field",
    [
        "strategy_version",
        "config_version",
        "config_fingerprint",
        "instrument_id",
        "timeframe",
        "state_schema_version",
    ],
)
def test_snapshot_identity_config_scope_or_schema_mismatch_halts(
    field,
):
    (
        _,
        snapshot,
        _,
    ) = setup()

    replacement = {
        "strategy_version": "2",
        "config_version": "C2",
        "config_fingerprint": (
            "0" * 64
        ),
        "instrument_id": 2,
        "timeframe": "5m",
        "state_schema_version": 2,
    }[field]

    result, _ = recover(
        snapshot_override=(
            snapshot.model_copy(
                update={
                    field: replacement,
                }
            )
        )
    )

    assert (
        result.state
        is RecoveryReadinessState.HALT
    )


def test_decode_restore_failure_halts():
    (
        _,
        snapshot,
        _,
    ) = setup()

    broken = snapshot.model_copy(
        update={
            "state_json": {
                "schema_version": 1,
                "unexpected": True,
            }
        }
    )

    result, _ = recover(
        snapshot_override=broken
    )

    assert (
        result.state
        is RecoveryReadinessState.HALT
    )


def test_arbitrary_legacy_bar_reference_cannot_authorize_ready():
    result, trace = recover(
        required_revision=None,
        legacy_required="BAR-1",
    )

    assert (
        result.state
        is RecoveryReadinessState.HALT
    )

    assert trace == [
        "execution",
        "expected",
        "broker",
    ]


def test_valid_mor1_legacy_parameter_is_bounded_compatibility():
    result, _ = recover(
        required_revision=None,
        legacy_required=MOR1_A,
    )

    assert (
        result.state
        is RecoveryReadinessState.REVIEW
    )


def test_conflicting_legacy_canonical_required_reference_halts():
    result, _ = recover(
        required_revision=MOR1_A,
        legacy_required=MOR1_B,
    )

    assert (
        result.state
        is RecoveryReadinessState.HALT
    )


def test_canonical_revision_mismatch_halts():
    result, _ = recover(
        required_revision=MOR1_B,
    )

    assert (
        result.state
        is RecoveryReadinessState.HALT
    )


def test_c16_missing_binding_provenance_halts_before_snapshot_restore():
    result, trace = recover(
        instance_transform=lambda item: item.model_copy(
            update={"instrument_binding_provenance": None}
        )
    )

    assert result.state is RecoveryReadinessState.HALT
    assert "durable canonical instrument binding provenance" in result.reasons[0]
    assert "state" not in trace


def test_c16_implementation_revision_mismatch_halts_before_snapshot_restore():
    result, trace = recover(
        instance_transform=lambda item: item.model_copy(
            update={"strategy_version": "2.0.0"}
        )
    )

    assert result.state is RecoveryReadinessState.HALT
    assert "implementation revision mismatch" in result.reasons[0]
    assert "state" not in trace


def test_c16_same_config_version_changed_config_fails_against_durable_snapshot():
    def mutate(item):
        changed = {
            "symbol": "MTX",
            "timeframe": "1m",
        }
        return item.model_copy(
            update={
                "config_json": changed,
                "config_fingerprint": config_fingerprint(changed),
            }
        )

    result, trace = recover(instance_transform=mutate)

    assert result.state is RecoveryReadinessState.HALT
    assert "identity/config/scope/revision mismatch" in result.reasons[0]
    assert "state" in trace


def test_c16_binding_provenance_does_not_use_current_alias_to_remap_history():
    def alias_drift(item):
        changed = {
            "symbol": "TODAYS-ALIAS",
            "timeframe": "1m",
        }
        return item.model_copy(
            update={
                "config_version": "C2",
                "config_json": changed,
                "config_fingerprint": config_fingerprint(changed),
            }
        )

    result, _ = recover(instance_transform=alias_drift)

    assert result.state is RecoveryReadinessState.HALT
    assert "identity/config/scope/revision mismatch" in result.reasons[0]


def test_c16_rf01_corrupted_config_content_halts_before_strategy_restore() -> None:
    def corrupt_config(item):
        return item.model_copy(
            update={
                "config_json": {
                    "symbol": "MTX",
                    "timeframe": "1m",
                }
            }
        )

    result, trace = recover(
        instance_transform=corrupt_config
    )

    assert result.state is RecoveryReadinessState.HALT
    assert "governing config fingerprint" in result.reasons[0]
    assert trace == [
        "execution",
        "expected",
        "broker",
        "instance",
    ]


def _c17_transition_authority(
    state_name,
):
    from strategy.recovery import (
        StrategyAuthorityRef,
        StrategyDurableStateReference,
        StrategyGoverningContext,
        StrategyGoverningTransitionAuthority,
        StrategyGoverningTransitionState,
        StrategyStateSchemaReference,
    )

    item, source_snapshot, _ = setup()

    source = StrategyGoverningContext(
        strategy_instance_id=item.strategy_instance_id,
        strategy_id=item.strategy_id,
        config_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-CONFIG",
            authority_version="C1-AUTH",
        ),
        config_version=item.config_version,
        config_fingerprint=item.config_fingerprint,
        implementation_revision=item.strategy_version,
        instrument_id=item.instrument_id,
        instrument_binding_provenance=(
            item.instrument_binding_provenance
        ),
        timeframe=item.timeframe,
        decision_policy_version="DP-1",
        state_schema_reference=StrategyStateSchemaReference(
            strategy_id=item.strategy_id,
            schema_version=source_snapshot.state_schema_version,
        ),
    )

    target_config = {
        "symbol": "TX",
        "timeframe": "1m",
        "mode": "target",
    }
    target_fingerprint = config_fingerprint(
        target_config
    )

    target = StrategyGoverningContext(
        strategy_instance_id=item.strategy_instance_id,
        strategy_id=item.strategy_id,
        config_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-CONFIG",
            authority_version="C2-AUTH",
        ),
        config_version="C2",
        config_fingerprint=target_fingerprint,
        implementation_revision=item.strategy_version,
        instrument_id=item.instrument_id,
        instrument_binding_provenance=(
            item.instrument_binding_provenance
        ),
        timeframe=item.timeframe,
        decision_policy_version="DP-2",
        state_schema_reference=StrategyStateSchemaReference(
            strategy_id=item.strategy_id,
            schema_version=2,
        ),
    )

    target_state = StrategyDurableStateReference(
        snapshot_id="SS-TARGET",
        strategy_instance_id=item.strategy_instance_id,
        strategy_id=item.strategy_id,
        config_version="C2",
        config_fingerprint=target_fingerprint,
        implementation_revision=item.strategy_version,
        instrument_id=item.instrument_id,
        timeframe=item.timeframe,
        state_schema_reference=StrategyStateSchemaReference(
            strategy_id=item.strategy_id,
            schema_version=2,
        ),
    )

    state = StrategyGoverningTransitionState(
        state_name
    )
    values = dict(
        transition_id="TR-C17-RECOVERY",
        strategy_instance_id=item.strategy_instance_id,
        source_context=source,
        target_context=target,
        compatibility_authority=StrategyAuthorityRef(
            authority_id="STRATEGY-COMPATIBILITY",
            authority_version="V1",
        ),
        migration_authority=StrategyAuthorityRef(
            authority_id="STATE-MIGRATION",
            authority_version="V1",
        ),
        transition_policy=StrategyAuthorityRef(
            authority_id="GOVERNING-TRANSITION",
            authority_version="V1",
        ),
    )

    if state is StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS:
        values["begin_effective_boundary_ref"] = "BEGIN-1"
    elif state is StrategyGoverningTransitionState.POST_TRANSITION:
        values["begin_effective_boundary_ref"] = "BEGIN-1"
        values["completion_boundary_ref"] = "COMPLETE-1"
        values["established_target_state"] = target_state

    return (
        StrategyGoverningTransitionAuthority(**values),
        source_snapshot,
        target_state,
        target_fingerprint,
    )


def test_c17_pre_transition_preserves_source_restore_path() -> None:
    authority, _, _, _ = _c17_transition_authority(
        "PRE_TRANSITION"
    )

    result, trace = recover(
        transition_authority=authority,
        use_transition_repository=True,
    )

    assert result.state is RecoveryReadinessState.REVIEW
    assert isinstance(
        result.restored_strategies[0],
        EMACrossStrategy,
    )
    assert trace == [
        "execution",
        "expected",
        "broker",
        "instance",
        "state",
        "transition",
    ]


def test_c17_transition_in_progress_cannot_restore_normal_runtime() -> None:
    authority, _, _, _ = _c17_transition_authority(
        "TRANSITION_IN_PROGRESS"
    )

    result, trace = recover(
        transition_authority=authority,
        use_transition_repository=True,
    )

    assert result.state is RecoveryReadinessState.REVIEW
    assert result.restored_strategies == ()
    assert "transition is in progress" in result.reasons[0]
    assert trace[-1] == "transition"


def test_c17_post_transition_does_not_auto_claim_strategy_ready() -> None:
    authority, source_snapshot, _, target_fingerprint = (
        _c17_transition_authority(
            "POST_TRANSITION"
        )
    )

    target_snapshot = source_snapshot.model_copy(
        update={
            "snapshot_id": "SS-TARGET",
            "config_version": "C2",
            "config_fingerprint": target_fingerprint,
            "state_schema_version": 2,
        }
    )

    result, trace = recover(
        snapshot_override=target_snapshot,
        transition_authority=authority,
        use_transition_repository=True,
    )

    assert result.state is RecoveryReadinessState.REVIEW
    assert result.restored_strategies == ()
    assert "later readiness composition" in result.reasons[0]
    assert trace[-1] == "transition"
