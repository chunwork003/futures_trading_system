
from __future__ import annotations

import hashlib
import json
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
    ReconciliationInputQualification,
    ReconciliationRunBoundary,
    ReconciliationRunOutcome,
    ReconciliationRunTechnicalOutcome,
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
    ReconciliationStatus,
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
    broker_report_witness: tuple[str, ...] = ()
    current_nonterminal_order_anchors: tuple[str, ...] = ()
    fill_event_validation_anchors: tuple[str, ...] = ()
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
        if self.head.current_revision != self.checkpoint.account_revision:
            raise ValueError("RecoveryCut requires exact head revision closure")
        if (self.recovery_generation is None) != (self.recovery_ingress_version is None):
            raise ValueError("recovery control witness must be complete")
        for name in (
            "broker_report_witness",
            "current_nonterminal_order_anchors",
            "fill_event_validation_anchors",
            "unresolved_broker_action_ids",
        ):
            values=getattr(self,name)
            normalized=tuple(value.strip() for value in values)
            if any(not value for value in normalized) or normalized != tuple(sorted(set(normalized))):
                raise ValueError(f"{name} must contain sorted unique nonblank values")
        return self

    @property
    def witness_fingerprint(self) -> str:
        """把 exact revision 與非 revision witness 固定成可重驗的 deterministic fingerprint。"""

        canonical=json.dumps(self.model_dump(mode="json"),ensure_ascii=False,sort_keys=True,separators=(",",":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


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


class AccountReadinessEvidence(BaseModel):
    """C15 純 local readiness inputs；每個 mandatory predicate 必須有正向證據，UNKNOWN 不得升級 READY。"""

    model_config=ConfigDict(extra="forbid",frozen=True)

    restore_result: ExecutionRestoreResult
    formal_run_boundary: ReconciliationRunBoundary | None
    formal_run_outcome: ReconciliationRunOutcome | None
    required_policy: ReconciliationPolicy = ReconciliationPolicy.STRICT_HALT
    result_completeness_evidence: tuple[str, ...] = ()
    discovery_complete: bool
    exact_correlation_integrity: bool
    continuity_current: bool
    pending_material_inbox: bool
    reconstruction_complete: bool
    reconstruction_conflict: bool
    mandatory_capabilities_available: bool
    out_of_horizon_unresolved_action: bool = False

    @model_validator(mode="after")
    def _normalize_completeness_evidence(self) -> "AccountReadinessEvidence":
        normalized=tuple(value.strip() for value in self.result_completeness_evidence)
        if any(not value for value in normalized):
            raise ValueError("result completeness evidence must be nonblank")
        object.__setattr__(self,"result_completeness_evidence",normalized)
        return self


class AccountReadinessEvaluation(BaseModel):
    """BrokerAccount READY/REVIEW/HALT evaluation；保存 exact cut witness 供 final local revalidation。"""

    model_config=ConfigDict(extra="forbid",frozen=True)

    state: RecoveryReadinessState
    reasons: tuple[str,...]
    account: BrokerAccount
    account_revision: int = Field(ge=0)
    recovery_generation: int | None = Field(default=None,ge=1)
    recovery_ingress_version: int | None = Field(default=None,ge=0)
    inbox_count: int = Field(ge=0)
    application_count: int = Field(ge=0)
    recovery_cut_fingerprint: str
    broker_report_witness: tuple[str,...]
    current_nonterminal_order_anchors: tuple[str,...]
    fill_event_validation_anchors: tuple[str,...]
    unresolved_broker_action_ids: tuple[str,...]


def evaluate_account_readiness(*,account: BrokerAccount,evidence: AccountReadinessEvidence) -> AccountReadinessEvaluation:
    """依 HALT > REVIEW > READY 聚合 frozen predicates；不 repair、不呼叫 broker、不授權交易。"""

    restore=evidence.restore_result
    if restore.status is not ExecutionRestoreStatus.VALID or restore.cut is None:
        return AccountReadinessEvaluation(state=RecoveryReadinessState.HALT,reasons=("coherent recovery cut is not valid",),account=account,account_revision=0,inbox_count=0,application_count=0,recovery_cut_fingerprint="INVALID",broker_report_witness=(),current_nonterminal_order_anchors=(),fill_event_validation_anchors=(),unresolved_broker_action_ids=())
    cut=restore.cut
    common=dict(account=account,account_revision=cut.head.current_revision,recovery_generation=cut.recovery_generation,recovery_ingress_version=cut.recovery_ingress_version,inbox_count=cut.inbox_count,application_count=cut.application_count,recovery_cut_fingerprint=cut.witness_fingerprint,broker_report_witness=cut.broker_report_witness,current_nonterminal_order_anchors=cut.current_nonterminal_order_anchors,fill_event_validation_anchors=cut.fill_event_validation_anchors,unresolved_broker_action_ids=cut.unresolved_broker_action_ids)
    halt=[]
    if cut.account != account: halt.append("requested BrokerAccount does not match recovery cut")
    if not evidence.mandatory_capabilities_available: halt.append("mandatory capability unavailable")
    if not evidence.exact_correlation_integrity: halt.append("broker correlation integrity conflict")
    if evidence.reconstruction_conflict: halt.append("canonical reconstruction integrity conflict")
    outcome=evidence.formal_run_outcome
    boundary=evidence.formal_run_boundary
    if boundary is None: halt.append("eligible formal reconciliation run boundary is missing")
    elif (
        boundary.account != account
        or boundary.account != cut.account
        or boundary.policy is not evidence.required_policy
        or boundary.recovery_cut_fingerprint != cut.witness_fingerprint
        or boundary.account_revision != cut.head.current_revision
        or boundary.expected_snapshot_id != cut.checkpoint.expected_snapshot_id
        or boundary.authority_commit_id != cut.checkpoint.authority_commit_id
        or boundary.recovery_generation != cut.recovery_generation
        or boundary.recovery_ingress_version != cut.recovery_ingress_version
        or boundary.discovery_run_id is None
        or boundary.observation_id is None
    ): halt.append("formal reconciliation run boundary does not bind the current recovery cut")
    if outcome is None: halt.append("eligible formal reconciliation run is missing")
    elif boundary is not None and outcome.run_id != boundary.run_id: halt.append("formal reconciliation outcome does not bind the established run")
    elif outcome.technical_outcome is ReconciliationRunTechnicalOutcome.FAILED: halt.append("formal reconciliation run failed")
    if halt:
        return AccountReadinessEvaluation(state=RecoveryReadinessState.HALT,reasons=tuple(halt),**common)
    review=[]
    if not evidence.discovery_complete: review.append("broker discovery is incomplete")
    if not evidence.continuity_current: review.append("execution continuity is not current")
    if evidence.pending_material_inbox: review.append("material broker inbox evidence is pending")
    if not evidence.reconstruction_complete: review.append("canonical reconstruction is incomplete")
    if cut.unresolved_broker_action_ids: review.append("broker action disposition is unresolved")
    if evidence.out_of_horizon_unresolved_action: review.append("broker action requires external disposition evidence")
    if outcome is not None and not outcome.results and not evidence.result_completeness_evidence:
        review.append("empty reconciliation result lacks positive completeness evidence")
    if outcome is not None and (
        outcome.input_qualification is not ReconciliationInputQualification.QUALIFIED
        or outcome.technical_outcome is not ReconciliationRunTechnicalOutcome.COMPLETED
        or any(result.status is not ReconciliationStatus.MATCH for result in outcome.results)
    ): review.append("formal reconciliation is not a qualified MATCH")
    if review:
        return AccountReadinessEvaluation(state=RecoveryReadinessState.REVIEW,reasons=tuple(review),**common)
    return AccountReadinessEvaluation(state=RecoveryReadinessState.READY,reasons=(),**common)


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

    restore_result=execution_loader.load(account)
    if not isinstance(restore_result,ExecutionRestoreResult) or restore_result.status is not ExecutionRestoreStatus.VALID:
        return RecoveryResult(state=RecoveryReadinessState.HALT,reasons=("legacy recovery lacks a valid coherent RecoveryCut",))

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
        case_repository.unresolved(account)
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
        state=RecoveryReadinessState.REVIEW,
        reasons=("legacy recovery lacks eligible formal reconciliation/currentness evidence",),
        restored_strategies=tuple(
            restored
        ),
    )
