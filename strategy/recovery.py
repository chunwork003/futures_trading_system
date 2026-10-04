from __future__ import annotations

from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from persistence.contracts import normalize_stable_id
from strategy.instance import (
    CanonicalInstrumentBindingProvenance,
    StrategyInstance,
)


class StrategyGoverningTransitionState(str, Enum):
    """C17 唯一允許的三種 governing-context recovery classification。"""

    PRE_TRANSITION = "PRE_TRANSITION"
    TRANSITION_IN_PROGRESS = "TRANSITION_IN_PROGRESS"
    POST_TRANSITION = "POST_TRANSITION"


class StrategyGoverningTransitionIntegrityError(ValueError):
    """C17 authority/context/state 混合或不一致時 fail closed。"""


class StrategyAuthorityRef(BaseModel):
    """不可變 authority identity + version reference；本身不代表 readiness。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    authority_id: str
    authority_version: str

    @field_validator(
        "authority_id",
        "authority_version",
        mode="before",
    )
    @classmethod
    def _stable_ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value


class StrategyStateSchemaReference(BaseModel):
    """以 governing StrategyDefinition identity + schema version 綁定 state schema。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    strategy_id: str
    schema_version: int = Field(ge=1)

    @field_validator("strategy_id", mode="before")
    @classmethod
    def _strategy_id(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value


class StrategyGoverningContext(BaseModel):
    """C17 transition 一側的完整 governing authority context。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    strategy_instance_id: str
    strategy_id: str
    config_authority: StrategyAuthorityRef
    config_version: str
    config_fingerprint: str
    implementation_revision: str
    instrument_id: int = Field(gt=0)
    instrument_binding_provenance: CanonicalInstrumentBindingProvenance
    timeframe: str
    decision_policy_version: str | None = None
    state_schema_reference: StrategyStateSchemaReference

    @field_validator(
        "strategy_instance_id",
        "strategy_id",
        "config_version",
        "config_fingerprint",
        "implementation_revision",
        "timeframe",
        mode="before",
    )
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("decision_policy_version", mode="before")
    @classmethod
    def _optional_policy(cls, value: object) -> object:
        if value is None:
            return None
        return normalize_stable_id(value) if isinstance(value, str) else value

    @model_validator(mode="after")
    def _scope_integrity(self) -> "StrategyGoverningContext":
        if self.instrument_binding_provenance.instrument_id != self.instrument_id:
            raise ValueError(
                "governing context instrument binding provenance conflicts "
                "with canonical instrument_id"
            )
        if self.state_schema_reference.strategy_id != self.strategy_id:
            raise ValueError(
                "state schema reference conflicts with governing StrategyDefinition"
            )
        return self


class StrategyDurableStateReference(BaseModel):
    """C17 對 durable StrategyStateSnapshot 的 broker-neutral exact reference。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    snapshot_id: str
    strategy_instance_id: str
    strategy_id: str
    config_version: str
    config_fingerprint: str
    implementation_revision: str
    instrument_id: int = Field(gt=0)
    timeframe: str
    state_schema_reference: StrategyStateSchemaReference

    @field_validator(
        "snapshot_id",
        "strategy_instance_id",
        "strategy_id",
        "config_version",
        "config_fingerprint",
        "implementation_revision",
        "timeframe",
        mode="before",
    )
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value


def _state_matches_context(
    state: StrategyDurableStateReference,
    context: StrategyGoverningContext,
) -> bool:
    return (
        state.strategy_instance_id == context.strategy_instance_id
        and state.strategy_id == context.strategy_id
        and state.config_version == context.config_version
        and state.config_fingerprint == context.config_fingerprint
        and state.implementation_revision == context.implementation_revision
        and state.instrument_id == context.instrument_id
        and state.timeframe == context.timeframe
        and state.state_schema_reference == context.state_schema_reference
    )


def _source_matches_instance(
    source: StrategyGoverningContext,
    instance: StrategyInstance,
) -> bool:
    return (
        source.strategy_instance_id == instance.strategy_instance_id
        and source.strategy_id == instance.strategy_id
        and source.config_version == instance.config_version
        and source.config_fingerprint == instance.config_fingerprint
        and source.implementation_revision == instance.implementation_revision
        and source.instrument_id == instance.instrument_id
        and source.instrument_binding_provenance
        == instance.instrument_binding_provenance
        and source.timeframe == instance.timeframe
    )


class StrategyGoverningTransitionAuthority(BaseModel):
    """C17 durable transition authority；classification 僅由 durable boundaries 決定。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    transition_id: str
    strategy_instance_id: str
    source_context: StrategyGoverningContext
    target_context: StrategyGoverningContext
    compatibility_authority: StrategyAuthorityRef
    migration_authority: StrategyAuthorityRef | None = None
    transition_policy: StrategyAuthorityRef
    begin_effective_boundary_ref: str | None = None
    completion_boundary_ref: str | None = None
    established_target_state: StrategyDurableStateReference | None = None

    @field_validator(
        "transition_id",
        "strategy_instance_id",
        mode="before",
    )
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator(
        "begin_effective_boundary_ref",
        "completion_boundary_ref",
        mode="before",
    )
    @classmethod
    def _optional_ids(cls, value: object) -> object:
        if value is None:
            return None
        return normalize_stable_id(value) if isinstance(value, str) else value

    @model_validator(mode="after")
    def _transition_integrity(self) -> "StrategyGoverningTransitionAuthority":
        if (
            self.source_context.strategy_instance_id != self.strategy_instance_id
            or self.target_context.strategy_instance_id != self.strategy_instance_id
        ):
            raise ValueError(
                "transition source/target context conflicts with StrategyInstance identity"
            )

        if self.source_context == self.target_context:
            raise ValueError(
                "governing transition must change source/target context"
            )

        established = self.established_target_state
        if established is not None and not _state_matches_context(
            established,
            self.target_context,
        ):
            raise ValueError(
                "established target durable state conflicts with target governing context"
            )

        if self.begin_effective_boundary_ref is None:
            if self.completion_boundary_ref is not None or established is not None:
                raise ValueError(
                    "transition evidence exists before durable begin/effective boundary"
                )
        elif (
            self.completion_boundary_ref is not None
            and established is None
        ):
            raise ValueError(
                "completed transition requires exact target-compatible durable state"
            )

        return self

    @property
    def state(self) -> StrategyGoverningTransitionState:
        if self.begin_effective_boundary_ref is None:
            return StrategyGoverningTransitionState.PRE_TRANSITION
        if self.completion_boundary_ref is None:
            return StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS
        return StrategyGoverningTransitionState.POST_TRANSITION


def evaluate_governing_transition(
    *,
    authority: StrategyGoverningTransitionAuthority,
    source_instance: StrategyInstance,
    durable_state: StrategyDurableStateReference,
) -> StrategyGoverningTransitionState:
    """重啟時以 exact durable authority 分類 C17；不授予 StrategyTradingReady。"""

    if authority.strategy_instance_id != source_instance.strategy_instance_id:
        raise StrategyGoverningTransitionIntegrityError(
            "transition authority conflicts with requested StrategyInstance"
        )

    if not _source_matches_instance(
        authority.source_context,
        source_instance,
    ):
        raise StrategyGoverningTransitionIntegrityError(
            "transition source governing context conflicts with C16 authority"
        )

    state = authority.state

    if state is StrategyGoverningTransitionState.PRE_TRANSITION:
        if not _state_matches_context(
            durable_state,
            authority.source_context,
        ):
            raise StrategyGoverningTransitionIntegrityError(
                "PRE_TRANSITION durable state does not match source governing context"
            )
        return state

    if state is StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS:
        if _state_matches_context(
            durable_state,
            authority.source_context,
        ):
            return state

        established = authority.established_target_state
        if (
            established is not None
            and durable_state == established
            and _state_matches_context(
                durable_state,
                authority.target_context,
            )
        ):
            return state

        raise StrategyGoverningTransitionIntegrityError(
            "TRANSITION_IN_PROGRESS exposes mixed incompatible governing state"
        )

    established = authority.established_target_state
    if (
        established is None
        or durable_state != established
        or not _state_matches_context(
            durable_state,
            authority.target_context,
        )
    ):
        raise StrategyGoverningTransitionIntegrityError(
            "POST_TRANSITION target-compatible durable state is missing or mismatched"
        )

    return state



class K520ApplicabilityClassification(str, Enum):
    """C19 K520 applicability seam；不代表 K520 recovery 已完成。"""

    NOT_APPLICABLE_PROVEN = "NOT_APPLICABLE_PROVEN"
    REQUIRED = "REQUIRED"
    UNKNOWN = "UNKNOWN"


class K520ApplicabilityEvidence(BaseModel):
    """C19 broker-neutral positive applicability evidence。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_id: str
    strategy_instance_id: str
    strategy_id: str
    config_version: str
    config_fingerprint: str
    implementation_revision: str
    instrument_id: int = Field(gt=0)
    instrument_binding_provenance: CanonicalInstrumentBindingProvenance
    timeframe: str

    feature_dependency_contract: StrategyAuthorityRef | None = None
    classification_claim: K520ApplicabilityClassification = (
        K520ApplicabilityClassification.UNKNOWN
    )

    required_replay_horizon: int | None = Field(default=None, ge=0)
    available_replay_horizon: int | None = Field(default=None, ge=0)

    governing_observation_frontier_revision_id: str | None = None
    evaluated_observation_frontier_revision_id: str | None = None
    current_observation_frontier_revision_id: str | None = None

    causal_frontier_ref: str | None = None
    currentness_evidence_ref: str | None = None
    proof_authority: StrategyAuthorityRef | None = None

    @field_validator(
        "evidence_id",
        "strategy_instance_id",
        "strategy_id",
        "config_version",
        "config_fingerprint",
        "implementation_revision",
        "timeframe",
        mode="before",
    )
    @classmethod
    def _stable_ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator(
        "causal_frontier_ref",
        "currentness_evidence_ref",
        mode="before",
    )
    @classmethod
    def _optional_ids(cls, value: object) -> object:
        if value is None:
            return None
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator(
        "governing_observation_frontier_revision_id",
        "evaluated_observation_frontier_revision_id",
        "current_observation_frontier_revision_id",
        mode="before",
    )
    @classmethod
    def _mor1_refs(cls, value: object) -> object:
        if value is None:
            return None

        from domain.market_observation import MarketObservationRevisionId

        if isinstance(value, MarketObservationRevisionId):
            return value.value

        if not isinstance(value, str):
            raise ValueError(
                "K520 observation frontier must use mor1 revision identity"
            )

        normalized = normalize_stable_id(value)

        try:
            return MarketObservationRevisionId(normalized).value
        except ValueError as exc:
            raise ValueError(
                "K520 observation frontier must use mor1 revision identity"
            ) from exc

    @model_validator(mode="after")
    def _binding_integrity(self) -> "K520ApplicabilityEvidence":
        if (
            self.instrument_binding_provenance.instrument_id
            != self.instrument_id
        ):
            raise ValueError(
                "K520 applicability instrument provenance conflicts "
                "with canonical instrument_id"
            )
        return self


def evaluate_k520_applicability(
    *,
    instance: StrategyInstance,
    evidence: K520ApplicabilityEvidence,
) -> K520ApplicabilityClassification:
    """依 exact C16 recovery world 評估 C19；任何未證明條件皆 UNKNOWN。"""

    provenance = instance.instrument_binding_provenance

    if provenance is None:
        return K520ApplicabilityClassification.UNKNOWN

    exact_governing_binding = (
        evidence.strategy_instance_id == instance.strategy_instance_id
        and evidence.strategy_id == instance.strategy_id
        and evidence.config_version == instance.config_version
        and evidence.config_fingerprint == instance.config_fingerprint
        and evidence.implementation_revision == instance.implementation_revision
        and evidence.instrument_id == instance.instrument_id
        and evidence.instrument_binding_provenance == provenance
        and evidence.timeframe == instance.timeframe
    )

    if not exact_governing_binding:
        return K520ApplicabilityClassification.UNKNOWN

    if evidence.classification_claim is K520ApplicabilityClassification.UNKNOWN:
        return K520ApplicabilityClassification.UNKNOWN

    if (
        evidence.feature_dependency_contract is None
        or evidence.proof_authority is None
        or evidence.required_replay_horizon is None
        or evidence.available_replay_horizon is None
        or evidence.causal_frontier_ref is None
        or evidence.currentness_evidence_ref is None
        or evidence.governing_observation_frontier_revision_id is None
        or evidence.evaluated_observation_frontier_revision_id is None
        or evidence.current_observation_frontier_revision_id is None
    ):
        return K520ApplicabilityClassification.UNKNOWN

    if evidence.available_replay_horizon < evidence.required_replay_horizon:
        return K520ApplicabilityClassification.UNKNOWN

    frontier = evidence.governing_observation_frontier_revision_id

    if (
        evidence.evaluated_observation_frontier_revision_id != frontier
        or evidence.current_observation_frontier_revision_id != frontier
    ):
        return K520ApplicabilityClassification.UNKNOWN

    return evidence.classification_claim



class CompletenessRequirementClassification(str, Enum):
    """C20 completeness-required authority classification。"""

    NOT_REQUIRED_PROVEN = "NOT_REQUIRED_PROVEN"
    REQUIRED = "REQUIRED"
    UNKNOWN = "UNKNOWN"


class CompletenessAuthorityClass(str, Enum):
    """C20 authority class；不同 environment 不得互相升格。"""

    TEST = "TEST"
    SANDBOX = "SANDBOX"
    PRODUCTION = "PRODUCTION"


class CompletenessReadiness(str, Enum):
    """C20 只輸出 completeness gate readiness，不代表 StrategyTradingReady。"""

    READY = "READY"
    NOT_READY = "NOT_READY"


class CompletenessRequirementAuthority(BaseModel):
    """C20 requirement authority；與 completeness evidence authority 嚴格分離。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    requirement_id: str
    consumer_ref: str
    scope_ref: str
    stream_ref: str
    horizon_ref: str
    policy_authority: StrategyAuthorityRef
    authority_class: CompletenessAuthorityClass
    classification: CompletenessRequirementClassification

    @field_validator(
        "requirement_id",
        "consumer_ref",
        "scope_ref",
        "stream_ref",
        "horizon_ref",
        mode="before",
    )
    @classmethod
    def _stable_ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value


class CompletenessEvidenceAuthority(BaseModel):
    """C20 approved completeness evidence；不實作 detector/service。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_id: str
    consumer_ref: str
    scope_ref: str
    stream_ref: str
    horizon_ref: str
    policy_authority: StrategyAuthorityRef
    authority_class: CompletenessAuthorityClass
    evaluated_world_ref: str
    current_world_ref: str
    evaluated_frontier_revision_id: str
    current_frontier_revision_id: str
    currentness_evidence_ref: str
    evidence_authority: StrategyAuthorityRef
    complete: bool

    @field_validator(
        "evidence_id",
        "consumer_ref",
        "scope_ref",
        "stream_ref",
        "horizon_ref",
        "evaluated_world_ref",
        "current_world_ref",
        "currentness_evidence_ref",
        mode="before",
    )
    @classmethod
    def _stable_ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator(
        "evaluated_frontier_revision_id",
        "current_frontier_revision_id",
        mode="before",
    )
    @classmethod
    def _mor1_refs(cls, value: object) -> str:
        from domain.market_observation import MarketObservationRevisionId

        if isinstance(value, MarketObservationRevisionId):
            return value.value

        if not isinstance(value, str):
            raise ValueError(
                "completeness frontier must use mor1 revision identity"
            )

        normalized = normalize_stable_id(value)

        try:
            return MarketObservationRevisionId(normalized).value
        except ValueError as exc:
            raise ValueError(
                "completeness frontier must use mor1 revision identity"
            ) from exc


def evaluate_completeness_readiness(
    *,
    requirement: CompletenessRequirementAuthority | None,
    evidence: CompletenessEvidenceAuthority | None,
    runtime_authority_class: CompletenessAuthorityClass,
) -> CompletenessReadiness:
    """C20 fail-closed seam；只驗證 approved authority，不執行 completeness detector。"""

    if requirement is None:
        return CompletenessReadiness.NOT_READY

    if requirement.authority_class is not runtime_authority_class:
        return CompletenessReadiness.NOT_READY

    if (
        requirement.classification
        is CompletenessRequirementClassification.UNKNOWN
    ):
        return CompletenessReadiness.NOT_READY

    if (
        requirement.classification
        is CompletenessRequirementClassification.NOT_REQUIRED_PROVEN
    ):
        return CompletenessReadiness.READY

    if evidence is None:
        return CompletenessReadiness.NOT_READY

    if evidence.authority_class is not runtime_authority_class:
        return CompletenessReadiness.NOT_READY

    exact_requirement_binding = (
        evidence.consumer_ref == requirement.consumer_ref
        and evidence.scope_ref == requirement.scope_ref
        and evidence.stream_ref == requirement.stream_ref
        and evidence.horizon_ref == requirement.horizon_ref
        and evidence.policy_authority == requirement.policy_authority
        and evidence.authority_class == requirement.authority_class
    )

    if not exact_requirement_binding:
        return CompletenessReadiness.NOT_READY

    if not evidence.complete:
        return CompletenessReadiness.NOT_READY

    if evidence.evaluated_world_ref != evidence.current_world_ref:
        return CompletenessReadiness.NOT_READY

    if (
        evidence.evaluated_frontier_revision_id
        != evidence.current_frontier_revision_id
    ):
        return CompletenessReadiness.NOT_READY

    return CompletenessReadiness.READY



class DecisionPolicyAuthorityClass(str, Enum):
    """C18 DecisionPolicy authority environment；不得跨環境升格。"""

    TEST = "TEST"
    SANDBOX = "SANDBOX"
    PRODUCTION = "PRODUCTION"


class BrokerAccountExecutionReadyInput(BaseModel):
    """C18 只消費既有 W4/C15 readiness；不重新實作 account readiness。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    authority_ref: str
    ready: bool

    @field_validator("authority_ref", mode="before")
    @classmethod
    def _authority_ref(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value


class StrategyRestoreValidEvidence(BaseModel):
    """Strategy restore validity 的 exact governing-context consumer evidence。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_id: str
    strategy_instance_id: str
    governing_context: StrategyGoverningContext
    restore_authority_ref: str
    valid: bool

    @field_validator(
        "evidence_id",
        "strategy_instance_id",
        "restore_authority_ref",
        mode="before",
    )
    @classmethod
    def _stable_ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @model_validator(mode="after")
    def _context_identity(self) -> "StrategyRestoreValidEvidence":
        if (
            self.governing_context.strategy_instance_id
            != self.strategy_instance_id
        ):
            raise ValueError(
                "restore evidence conflicts with StrategyInstance identity"
            )
        return self


class K520RecoveryEvidenceRef(BaseModel):
    """C18 僅消費 approved K520/GAP-09 evidence reference；不實作 K520。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_ref: str
    strategy_instance_id: str
    config_version: str
    config_fingerprint: str
    implementation_revision: str
    instrument_id: int = Field(gt=0)
    timeframe: str
    authority: StrategyAuthorityRef
    ready: bool

    @field_validator(
        "evidence_ref",
        "strategy_instance_id",
        "config_version",
        "config_fingerprint",
        "implementation_revision",
        "timeframe",
        mode="before",
    )
    @classmethod
    def _stable_ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value


class StrategyTradingReadinessEvaluation(BaseModel):
    """四層 readiness 中的 StrategyRestoreValid / StrategyTradingReady projection。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    strategy_instance_id: str
    broker_account_execution_ready: bool
    strategy_restore_valid: bool
    strategy_trading_ready: bool
    decision_policy_version: str | None = None
    reasons: tuple[str, ...] = ()

    @field_validator(
        "strategy_instance_id",
        mode="before",
    )
    @classmethod
    def _strategy_instance_id(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("decision_policy_version", mode="before")
    @classmethod
    def _policy_version(cls, value: object) -> object:
        if value is None:
            return None
        return normalize_stable_id(value) if isinstance(value, str) else value


class DecisionPolicyAuthorityRef(BaseModel):
    """G / Decision Domain owned policy 的 consumer-facing exact authority ref。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    policy_id: str
    policy_version: str
    authority: StrategyAuthorityRef
    authority_class: DecisionPolicyAuthorityClass

    @field_validator(
        "policy_id",
        "policy_version",
        mode="before",
    )
    @classmethod
    def _stable_ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value


class RequiredCohortMembershipEvidence(BaseModel):
    """C18 只消費 authoritative required-membership evidence，不定義 policy business semantics。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_id: str
    cohort_id: str
    policy: DecisionPolicyAuthorityRef
    required_strategy_instance_ids: tuple[str, ...]
    currentness_evidence_ref: str

    @field_validator(
        "evidence_id",
        "cohort_id",
        "currentness_evidence_ref",
        mode="before",
    )
    @classmethod
    def _stable_ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator(
        "required_strategy_instance_ids",
        mode="before",
    )
    @classmethod
    def _required_ids(cls, value: object) -> object:
        if isinstance(value, (tuple, list)):
            return tuple(
                normalize_stable_id(item)
                for item in value
            )
        return value

    @model_validator(mode="after")
    def _unique_required_members(self) -> "RequiredCohortMembershipEvidence":
        if (
            len(set(self.required_strategy_instance_ids))
            != len(self.required_strategy_instance_ids)
        ):
            raise ValueError(
                "required cohort membership contains duplicate StrategyInstance identity"
            )
        return self


class DecisionCohortTradingReadinessEvaluation(BaseModel):
    """C18 authoritative cohort composition result；不是 DecisionPolicy semantic owner。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    cohort_id: str | None = None
    decision_policy_version: str | None = None
    decision_cohort_trading_ready: bool
    required_strategy_instance_ids: tuple[str, ...] = ()
    missing_strategy_instance_ids: tuple[str, ...] = ()
    not_ready_strategy_instance_ids: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()

    @field_validator(
        "cohort_id",
        "decision_policy_version",
        mode="before",
    )
    @classmethod
    def _optional_ids(cls, value: object) -> object:
        if value is None:
            return None
        return normalize_stable_id(value) if isinstance(value, str) else value


class StartupCatchUpOutputKind(str, Enum):
    """Generic startup catch-up 可能產生的 output 類型；不含 R-02 exact causal replay。"""

    HISTORICAL_SIGNAL = "HISTORICAL_SIGNAL"
    NORMAL_BROKER_BOUND_ORDER_INTENT = "NORMAL_BROKER_BOUND_ORDER_INTENT"
    NORMAL_MATERIAL_PENDING = "NORMAL_MATERIAL_PENDING"
    NORMAL_BROKER_SIDE_EFFECT = "NORMAL_BROKER_SIDE_EFFECT"
    CURRENT_TRADABLE_DECISION = "CURRENT_TRADABLE_DECISION"


class StartupCatchUpIsolationEvaluation(BaseModel):
    """Generic catch-up 永遠位於 recovery isolation；不得直接授權正常 material action。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    output_kind: StartupCatchUpOutputKind
    recovery_isolated: bool
    normal_material_action_allowed: bool
    historical_signal_promotable: bool
    reason: str


def _context_matches_restore(
    *,
    context: StrategyGoverningContext,
    restore: StrategyRestoreValidEvidence,
) -> bool:
    return restore.governing_context == context


def _k520_evidence_matches_context(
    *,
    evidence: K520RecoveryEvidenceRef,
    context: StrategyGoverningContext,
) -> bool:
    return (
        evidence.strategy_instance_id == context.strategy_instance_id
        and evidence.config_version == context.config_version
        and evidence.config_fingerprint == context.config_fingerprint
        and evidence.implementation_revision == context.implementation_revision
        and evidence.instrument_id == context.instrument_id
        and evidence.timeframe == context.timeframe
    )


def evaluate_strategy_trading_readiness(
    *,
    instance: StrategyInstance,
    broker_account: BrokerAccountExecutionReadyInput,
    restore: StrategyRestoreValidEvidence,
    transition_state: StrategyGoverningTransitionState | None,
    transition_authority: StrategyGoverningTransitionAuthority | None,
    k520_applicability: K520ApplicabilityClassification,
    k520_evidence: K520RecoveryEvidenceRef | None,
    completeness_readiness: CompletenessReadiness,
) -> StrategyTradingReadinessEvaluation:
    """C18 Strategy readiness composition；BrokerAccount readiness 僅作為 input。"""

    reasons: list[str] = []

    if not broker_account.ready:
        reasons.append("BrokerAccountExecutionReady is false")

    if not restore.valid:
        reasons.append("StrategyRestoreValid is false")

    context = restore.governing_context

    if transition_state is None:
        if not _source_matches_instance(context, instance):
            reasons.append(
                "restore governing context is stale or mismatched against C16 authority"
            )
    else:
        if transition_authority is None:
            reasons.append(
                "governing transition classification lacks exact transition authority"
            )
        elif transition_state is StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS:
            reasons.append(
                "governing transition is in progress"
            )
        elif transition_state is StrategyGoverningTransitionState.PRE_TRANSITION:
            if (
                transition_authority.state
                is not StrategyGoverningTransitionState.PRE_TRANSITION
                or not _source_matches_instance(
                    transition_authority.source_context,
                    instance,
                )
                or not _context_matches_restore(
                    context=transition_authority.source_context,
                    restore=restore,
                )
            ):
                reasons.append(
                    "PRE_TRANSITION readiness does not bind exact source governing context"
                )
        elif transition_state is StrategyGoverningTransitionState.POST_TRANSITION:
            if (
                transition_authority.state
                is not StrategyGoverningTransitionState.POST_TRANSITION
                or not _context_matches_restore(
                    context=transition_authority.target_context,
                    restore=restore,
                )
            ):
                reasons.append(
                    "POST_TRANSITION readiness does not bind exact target governing context"
                )

    if k520_applicability is K520ApplicabilityClassification.UNKNOWN:
        reasons.append("K520 applicability is unknown")
    elif k520_applicability is K520ApplicabilityClassification.REQUIRED:
        if (
            k520_evidence is None
            or not k520_evidence.ready
            or not _k520_evidence_matches_context(
                evidence=k520_evidence,
                context=context,
            )
        ):
            reasons.append(
                "required K520 recovery evidence is missing, not ready, or mismatched"
            )

    if completeness_readiness is not CompletenessReadiness.READY:
        reasons.append("completeness dependency is not ready")

    ready = not reasons

    return StrategyTradingReadinessEvaluation(
        strategy_instance_id=instance.strategy_instance_id,
        broker_account_execution_ready=broker_account.ready,
        strategy_restore_valid=restore.valid,
        strategy_trading_ready=ready,
        decision_policy_version=context.decision_policy_version,
        reasons=tuple(reasons),
    )


def evaluate_decision_cohort_trading_readiness(
    *,
    membership: RequiredCohortMembershipEvidence | None,
    strategy_readiness: tuple[StrategyTradingReadinessEvaluation, ...],
    runtime_authority_class: DecisionPolicyAuthorityClass,
) -> DecisionCohortTradingReadinessEvaluation:
    """C18 cohort readiness 只依 authoritative membership；caller list 不成為 authority。"""

    if membership is None:
        return DecisionCohortTradingReadinessEvaluation(
            decision_cohort_trading_ready=False,
            reasons=(
                "authoritative governing DecisionPolicyVersion cohort evidence is missing",
            ),
        )

    if membership.policy.authority_class is not runtime_authority_class:
        return DecisionCohortTradingReadinessEvaluation(
            cohort_id=membership.cohort_id,
            decision_policy_version=membership.policy.policy_version,
            decision_cohort_trading_ready=False,
            required_strategy_instance_ids=(
                membership.required_strategy_instance_ids
            ),
            reasons=(
                "DecisionPolicy authority class does not match runtime environment",
            ),
        )

    by_id: dict[str, StrategyTradingReadinessEvaluation] = {}

    for item in strategy_readiness:
        if item.strategy_instance_id in by_id:
            raise ValueError(
                "duplicate StrategyInstance readiness cannot define cohort membership"
            )
        by_id[item.strategy_instance_id] = item

    required = membership.required_strategy_instance_ids
    missing = tuple(
        item
        for item in required
        if item not in by_id
    )
    not_ready = tuple(
        item
        for item in required
        if (
            item in by_id
            and (
                not by_id[item].strategy_trading_ready
                or by_id[item].decision_policy_version
                != membership.policy.policy_version
            )
        )
    )

    reasons: list[str] = []

    if missing:
        reasons.append(
            "required cohort StrategyInstance membership is missing"
        )

    if not_ready:
        reasons.append(
            "required cohort StrategyInstance is not ready under governing DecisionPolicyVersion"
        )

    return DecisionCohortTradingReadinessEvaluation(
        cohort_id=membership.cohort_id,
        decision_policy_version=membership.policy.policy_version,
        decision_cohort_trading_ready=not missing and not not_ready,
        required_strategy_instance_ids=required,
        missing_strategy_instance_ids=missing,
        not_ready_strategy_instance_ids=not_ready,
        reasons=tuple(reasons),
    )


def evaluate_generic_startup_catch_up_output(
    *,
    output_kind: StartupCatchUpOutputKind,
    action_label: str | None = None,
) -> StartupCatchUpIsolationEvaluation:
    """Generic startup catch-up 不是 normal/current evaluation；所有 material outputs 保持隔離。"""

    if action_label is not None:
        normalize_stable_id(action_label)

    return StartupCatchUpIsolationEvaluation(
        output_kind=output_kind,
        recovery_isolated=True,
        normal_material_action_allowed=False,
        historical_signal_promotable=False,
        reason=(
            "generic startup catch-up output remains recovery-isolated; "
            "normal material action requires a later current evaluation "
            "after StrategyTradingReady and DecisionCohortTradingReady"
        ),
    )


__all__ = [
    "BrokerAccountExecutionReadyInput",
    "CompletenessAuthorityClass",
    "DecisionCohortTradingReadinessEvaluation",
    "DecisionPolicyAuthorityClass",
    "DecisionPolicyAuthorityRef",
    "CompletenessAuthorityClass",
    "CompletenessEvidenceAuthority",
    "CompletenessReadiness",
    "CompletenessRequirementAuthority",
    "CompletenessRequirementClassification",
    "K520ApplicabilityClassification",
    "K520ApplicabilityEvidence",
    "K520RecoveryEvidenceRef",
    "RequiredCohortMembershipEvidence",
    "StartupCatchUpIsolationEvaluation",
    "StartupCatchUpOutputKind",
    "StrategyAuthorityRef",
    "StrategyDurableStateReference",
    "StrategyGoverningContext",
    "StrategyGoverningTransitionAuthority",
    "StrategyGoverningTransitionIntegrityError",
    "StrategyGoverningTransitionState",
    "StrategyRestoreValidEvidence",
    "StrategyStateSchemaReference",
    "StrategyTradingReadinessEvaluation",
    "evaluate_completeness_readiness",
    "evaluate_decision_cohort_trading_readiness",
    "evaluate_generic_startup_catch_up_output",
    "evaluate_governing_transition",
    "evaluate_k520_applicability",
    "evaluate_strategy_trading_readiness",
]
