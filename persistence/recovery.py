
from __future__ import annotations

from enum import Enum
from typing import (
    Protocol,
    runtime_checkable,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from persistence.account_authority import (
    AccountAuthorityCommitReceipt,
    AccountRecoveryCheckpoint,
    AccountStateHead,
    validate_authority_closure,
)

from persistence.reconciliation import (
    ReconciliationCaseRepository,
    blocking_case_state,
)
from persistence.strategy_state import (
    LegacyMarketObservationReferenceError,
    StrategyInstanceRepository,
    StrategyStateReferenceConflictError,
    StrategyStateRepository,
    normalize_market_observation_revision_id,
)
from strategy.registry import (
    StrategyRegistry,
)
from strategy.state import (
    StatefulStrategy,
)
from trading.account import (
    BrokerAccount,
    BrokerPositionProvider,
)
from trading.reconciliation import (
    ExpectedPositionLoader,
    ReconciliationCaseState,
    ReconciliationPolicy,
    StartupReadinessState,
    reconcile_startup,
)


class RecoveryReadinessState(
    str,
    Enum,
):
    READY = "READY"
    HALT = "HALT"
    REVIEW = "REVIEW"


class ExecutionRestoreStatus(str, Enum):
    """C12 local restore outcome；VALID 只代表 coherent local cut，不代表 READY。"""

    VALID = "VALID"
    BASELINE_NOT_ESTABLISHED = "BASELINE_NOT_ESTABLISHED"
    RESTORE_FAILURE = "RESTORE_FAILURE"


class RecoveryCut(BaseModel):
    """BrokerAccount-local immutable cut；封裝經濟 revision 與非 revision currentness witness。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    account: BrokerAccount
    head: AccountStateHead
    checkpoint: AccountRecoveryCheckpoint
    receipt: AccountAuthorityCommitReceipt
    recovery_generation: int | None = Field(default=None, ge=1)
    recovery_ingress_version: int | None = Field(default=None, ge=0)
    inbox_count: int = Field(ge=0)
    application_count: int = Field(ge=0)
    unresolved_broker_action_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _closure(self) -> "RecoveryCut":
        scope=(self.account.broker,self.account.account_ref)
        if scope != (self.head.broker,self.head.account_ref):
            raise ValueError("recovery cut account scope mismatch")
        validate_authority_closure(
            head=self.head,
            checkpoint=self.checkpoint,
            receipt=self.receipt,
        )
        if (self.recovery_generation is None) != (self.recovery_ingress_version is None):
            raise ValueError("recovery control witness must be complete")
        return self


class ExecutionRestoreResult(BaseModel):
    """ExecutionStateLoader 的明確 immutable 結果；partial diagnostics 不得冒充 VALID。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: ExecutionRestoreStatus
    cut: RecoveryCut | None = None
    evidence: tuple[str, ...]

    @model_validator(mode="after")
    def _status_contract(self) -> "ExecutionRestoreResult":
        if not self.evidence:
            raise ValueError("restore result requires positive evidence")
        if (self.status is ExecutionRestoreStatus.VALID) != (self.cut is not None):
            raise ValueError("only VALID restore result may contain a RecoveryCut")
        return self


class RecoveryResult(
    BaseModel
):
    """Restart recovery gate ?????? strategy?? repair broker/account?"""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        arbitrary_types_allowed=True,
    )

    state: RecoveryReadinessState
    reasons: tuple[
        str,
        ...,
    ] = ()
    restored_strategies: tuple[
        object,
        ...,
    ] = ()


@runtime_checkable
class ExecutionStateLoader(
    Protocol
):
    def load(
        self,
        account: BrokerAccount,
    ) -> ExecutionRestoreResult:
        ...


def _required_revision_id(
    *,
    required_market_observation_revision_id: (
        str
        | None
    ),
    required_market_observation_id: (
        str
        | None
    ),
) -> str:
    canonical = (
        None
        if (
            required_market_observation_revision_id
            is None
        )
        else (
            normalize_market_observation_revision_id(
                required_market_observation_revision_id
            )
        )
    )

    legacy = (
        None
        if (
            required_market_observation_id
            is None
        )
        else (
            normalize_market_observation_revision_id(
                required_market_observation_id
            )
        )
    )

    if (
        canonical is None
        and legacy is None
    ):
        raise (
            LegacyMarketObservationReferenceError(
                "required_market_observation_"
                "revision_id is required"
            )
        )

    if canonical is None:
        canonical = legacy

    if canonical is None:
        raise (
            LegacyMarketObservationReferenceError(
                "canonical market observation "
                "revision is required"
            )
        )

    if (
        legacy is not None
        and legacy != canonical
    ):
        raise (
            StrategyStateReferenceConflictError(
                "required legacy/canonical "
                "market observation references "
                "disagree"
            )
        )

    return canonical


def recover_runtime(
    *,
    account: BrokerAccount,
    execution_loader: ExecutionStateLoader,
    expected_loader: ExpectedPositionLoader,
    broker_position_provider: (
        BrokerPositionProvider
    ),
    reconciliation_policy: (
        ReconciliationPolicy
    ),
    case_repository: (
        ReconciliationCaseRepository
    ),
    strategy_instance_ids: tuple[
        str,
        ...,
    ],
    instance_repository: (
        StrategyInstanceRepository
    ),
    state_repository: (
        StrategyStateRepository
    ),
    registry: StrategyRegistry,
    required_market_observation_revision_id: (
        str
        | None
    ) = None,
    required_market_observation_id: (
        str
        | None
    ) = None,
) -> RecoveryResult:
    """Frozen ordering?exact canonical mor1 ?? restore strategy?"""

    execution_loader.load(
        account
    )

    account_result = (
        reconcile_startup(
            account=account,
            expected_loader=expected_loader,
            broker_position_provider=(
                broker_position_provider
            ),
            policy=(
                reconciliation_policy
            ),
            strategy_state_ready=True,
        )
    )

    if (
        account_result.state
        is StartupReadinessState.HALT
    ):
        return RecoveryResult(
            state=(
                RecoveryReadinessState.HALT
            ),
            reasons=(
                "account reconciliation halted",
            ),
        )

    if (
        account_result.state
        is StartupReadinessState.REVIEW
    ):
        return RecoveryResult(
            state=(
                RecoveryReadinessState.REVIEW
            ),
            reasons=(
                "account reconciliation "
                "requires review",
            ),
        )

    case_state = blocking_case_state(
        case_repository.unresolved()
    )

    if (
        case_state
        is ReconciliationCaseState.HALT
    ):
        return RecoveryResult(
            state=(
                RecoveryReadinessState.HALT
            ),
            reasons=(
                "persisted reconciliation "
                "HALT case",
            ),
        )

    if (
        case_state
        is (
            ReconciliationCaseState
            .REVIEW_REQUIRED
        )
    ):
        return RecoveryResult(
            state=(
                RecoveryReadinessState.REVIEW
            ),
            reasons=(
                "persisted reconciliation "
                "review case",
            ),
        )

    try:
        required_revision_id = (
            _required_revision_id(
                required_market_observation_revision_id=(
                    required_market_observation_revision_id
                ),
                required_market_observation_id=(
                    required_market_observation_id
                ),
            )
        )
    except (
        LegacyMarketObservationReferenceError,
        StrategyStateReferenceConflictError,
    ) as exc:
        return RecoveryResult(
            state=(
                RecoveryReadinessState.HALT
            ),
            reasons=(
                str(exc),
            ),
        )

    restored: list[
        object
    ] = []

    for (
        instance_id
    ) in strategy_instance_ids:
        instance = (
            instance_repository.get(
                instance_id
            )
        )

        try:
            snapshot = (
                state_repository.latest(
                    instance_id
                )
            )
        except (
            LegacyMarketObservationReferenceError,
            StrategyStateReferenceConflictError,
            ValueError,
        ) as exc:
            return RecoveryResult(
                state=(
                    RecoveryReadinessState.HALT
                ),
                reasons=(
                    str(exc),
                ),
            )

        if (
            instance is None
            or snapshot is None
        ):
            return RecoveryResult(
                state=(
                    RecoveryReadinessState.HALT
                ),
                reasons=(
                    "required strategy "
                    "instance/snapshot missing",
                ),
            )

        if (
            snapshot.strategy_instance_id
            != instance.strategy_instance_id
            or snapshot.strategy_id
            != instance.strategy_id
            or snapshot.strategy_version
            != instance.strategy_version
            or snapshot.config_version
            != instance.config_version
            or snapshot.config_fingerprint
            != instance.config_fingerprint
            or snapshot.instrument_id
            != instance.instrument_id
            or snapshot.timeframe
            != instance.timeframe
            or (
                snapshot
                .last_market_observation_revision_id
                != required_revision_id
            )
        ):
            return RecoveryResult(
                state=(
                    RecoveryReadinessState.HALT
                ),
                reasons=(
                    "strategy snapshot identity/"
                    "config/scope/revision mismatch",
                ),
            )

        try:
            strategy = (
                registry.create_instance(
                    instance
                )
            )

            if not isinstance(
                strategy,
                StatefulStrategy,
            ):
                raise ValueError(
                    "strategy does not expose "
                    "explicit state codec"
                )

            if (
                strategy.state_schema_version
                != snapshot.state_schema_version
            ):
                raise ValueError(
                    "strategy state schema mismatch"
                )

            strategy.restore_state(
                snapshot.state_json
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            return RecoveryResult(
                state=(
                    RecoveryReadinessState.HALT
                ),
                reasons=(
                    str(exc),
                ),
            )

        restored.append(
            strategy
        )

    return RecoveryResult(
        state=(
            RecoveryReadinessState.READY
        ),
        restored_strategies=tuple(
            restored
        ),
    )
