from __future__ import annotations

from enum import Enum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict

from persistence.reconciliation import ReconciliationCaseRepository, blocking_case_state
from persistence.strategy_state import StrategyInstanceRepository, StrategyStateRepository
from strategy.registry import StrategyRegistry
from strategy.state import StatefulStrategy
from trading.account import BrokerAccount, BrokerPositionProvider
from trading.reconciliation import (
    ExpectedPositionLoader,
    ReconciliationCaseState,
    ReconciliationPolicy,
    StartupReadinessState,
    reconcile_startup,
)


class RecoveryReadinessState(str, Enum):
    READY = "READY"
    HALT = "HALT"
    REVIEW = "REVIEW"


class RecoveryResult(BaseModel):
    """Restart recovery gate 結果；不啟動 strategy、不 repair broker/account。"""

    model_config = ConfigDict(extra="forbid", frozen=True, arbitrary_types_allowed=True)
    state: RecoveryReadinessState
    reasons: tuple[str, ...] = ()
    restored_strategies: tuple[object, ...] = ()


@runtime_checkable
class ExecutionStateLoader(Protocol):
    def load(self, account: BrokerAccount) -> None: ...


def recover_runtime(
    *,
    account: BrokerAccount,
    execution_loader: ExecutionStateLoader,
    expected_loader: ExpectedPositionLoader,
    broker_position_provider: BrokerPositionProvider,
    reconciliation_policy: ReconciliationPolicy,
    case_repository: ReconciliationCaseRepository,
    strategy_instance_ids: tuple[str, ...],
    instance_repository: StrategyInstanceRepository,
    state_repository: StrategyStateRepository,
    registry: StrategyRegistry,
    required_market_observation_id: str,
) -> RecoveryResult:
    """依 frozen ordering recovery；account gate 未通過前絕不 instantiate/restore strategy。"""

    execution_loader.load(account)
    account_result = reconcile_startup(
        account=account, expected_loader=expected_loader,
        broker_position_provider=broker_position_provider,
        policy=reconciliation_policy, strategy_state_ready=True,
    )
    if account_result.state is StartupReadinessState.HALT:
        return RecoveryResult(state=RecoveryReadinessState.HALT, reasons=("account reconciliation halted",))
    if account_result.state is StartupReadinessState.REVIEW:
        return RecoveryResult(state=RecoveryReadinessState.REVIEW, reasons=("account reconciliation requires review",))
    case_state = blocking_case_state(case_repository.unresolved())
    if case_state is ReconciliationCaseState.HALT:
        return RecoveryResult(state=RecoveryReadinessState.HALT, reasons=("persisted reconciliation HALT case",))
    if case_state is ReconciliationCaseState.REVIEW_REQUIRED:
        return RecoveryResult(state=RecoveryReadinessState.REVIEW, reasons=("persisted reconciliation review case",))

    restored: list[object] = []
    for instance_id in strategy_instance_ids:
        instance = instance_repository.get(instance_id)
        snapshot = state_repository.latest(instance_id)
        if instance is None or snapshot is None:
            return RecoveryResult(state=RecoveryReadinessState.HALT, reasons=("required strategy instance/snapshot missing",))
        if (
            snapshot.strategy_instance_id != instance.strategy_instance_id
            or snapshot.strategy_id != instance.strategy_id
            or snapshot.strategy_version != instance.strategy_version
            or snapshot.config_version != instance.config_version
            or snapshot.config_fingerprint != instance.config_fingerprint
            or snapshot.instrument_id != instance.instrument_id
            or snapshot.timeframe != instance.timeframe
            or snapshot.last_market_observation_id != required_market_observation_id
        ):
            return RecoveryResult(state=RecoveryReadinessState.HALT, reasons=("strategy snapshot identity/config/scope mismatch",))
        try:
            strategy = registry.create_instance(instance)
            if not isinstance(strategy, StatefulStrategy):
                raise ValueError("strategy does not expose explicit state codec")
            if strategy.state_schema_version != snapshot.state_schema_version:
                raise ValueError("strategy state schema mismatch")
            strategy.restore_state(snapshot.state_json)
        except (KeyError, TypeError, ValueError) as exc:
            return RecoveryResult(state=RecoveryReadinessState.HALT, reasons=(str(exc),))
        restored.append(strategy)
    return RecoveryResult(state=RecoveryReadinessState.READY, restored_strategies=tuple(restored))
