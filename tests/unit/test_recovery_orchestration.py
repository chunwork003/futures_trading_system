
from datetime import datetime, timezone

import pytest

from persistence.reconciliation import (
    ReconciliationCaseVersion,
)
from persistence.recovery import (
    RecoveryReadinessState,
    recover_runtime,
)
from persistence.strategy_state import (
    StrategyStateSnapshot,
)
from strategy.instance import (
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

    def unresolved(self):
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
):
    trace = []

    (
        item,
        snapshot,
        registry,
    ) = setup(
        snapshot_revision
    )

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


def test_successful_reconciliation_restores_strategy_and_is_ready():
    result, trace = recover()

    assert (
        result.state
        is RecoveryReadinessState.READY
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
        is RecoveryReadinessState.READY
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
