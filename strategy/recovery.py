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


__all__ = [
    "K520ApplicabilityClassification",
    "K520ApplicabilityEvidence",
    "StrategyAuthorityRef",
    "StrategyDurableStateReference",
    "StrategyGoverningContext",
    "StrategyGoverningTransitionAuthority",
    "StrategyGoverningTransitionIntegrityError",
    "StrategyGoverningTransitionState",
    "StrategyStateSchemaReference",
    "evaluate_governing_transition",
    "evaluate_k520_applicability",
]
