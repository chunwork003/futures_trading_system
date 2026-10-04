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
    """C17 immutable transition descriptor；phase progression 不得改寫 descriptor。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    transition_id: str
    strategy_instance_id: str
    source_context: StrategyGoverningContext
    target_context: StrategyGoverningContext
    compatibility_authority: StrategyAuthorityRef
    migration_authority: StrategyAuthorityRef | None = None
    transition_policy: StrategyAuthorityRef

    @field_validator("transition_id", "strategy_instance_id", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @model_validator(mode="after")
    def _descriptor_integrity(self) -> "StrategyGoverningTransitionAuthority":
        if (
            self.source_context.strategy_instance_id != self.strategy_instance_id
            or self.target_context.strategy_instance_id != self.strategy_instance_id
        ):
            raise ValueError(
                "transition source/target context conflicts with StrategyInstance identity"
            )
        if self.source_context == self.target_context:
            raise ValueError("governing transition must change source/target context")
        return self


class StrategyGoverningTransitionPhaseKind(str, Enum):
    """Pattern A append-only transition phase evidence kinds。"""

    BEGIN_EFFECTIVE = "BEGIN_EFFECTIVE"
    COMPLETION = "COMPLETION"


class StrategyGoverningTransitionPhaseEvidence(BaseModel):
    """同一 transition_id 下 immutable append-only phase/boundary evidence。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_id: str
    transition_id: str
    strategy_instance_id: str
    kind: StrategyGoverningTransitionPhaseKind
    boundary_ref: str
    evidence_authority: StrategyAuthorityRef
    established_target_state: StrategyDurableStateReference | None = None

    @field_validator(
        "evidence_id",
        "transition_id",
        "strategy_instance_id",
        "boundary_ref",
        mode="before",
    )
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @model_validator(mode="after")
    def _phase_shape(self) -> "StrategyGoverningTransitionPhaseEvidence":
        if (
            self.kind is StrategyGoverningTransitionPhaseKind.BEGIN_EFFECTIVE
            and self.established_target_state is not None
        ):
            raise ValueError("BEGIN_EFFECTIVE cannot establish target durable state")
        if (
            self.kind is StrategyGoverningTransitionPhaseKind.COMPLETION
            and self.established_target_state is None
        ):
            raise ValueError("COMPLETION requires exact established target durable state")
        return self


def classify_governing_transition(
    *,
    authority: StrategyGoverningTransitionAuthority,
    phase_evidence: tuple[StrategyGoverningTransitionPhaseEvidence, ...] = (),
) -> StrategyGoverningTransitionState:
    """只由 immutable descriptor + append-only phase evidence 分類三態。"""

    begin: StrategyGoverningTransitionPhaseEvidence | None = None
    completion: StrategyGoverningTransitionPhaseEvidence | None = None

    for item in phase_evidence:
        if (
            item.transition_id != authority.transition_id
            or item.strategy_instance_id != authority.strategy_instance_id
        ):
            raise StrategyGoverningTransitionIntegrityError(
                "phase evidence conflicts with transition identity"
            )

        if item.kind is StrategyGoverningTransitionPhaseKind.BEGIN_EFFECTIVE:
            if begin is not None:
                if begin != item:
                    raise StrategyGoverningTransitionIntegrityError(
                        "conflicting BEGIN_EFFECTIVE evidence"
                    )
                continue
            begin = item
        else:
            if completion is not None:
                if completion != item:
                    raise StrategyGoverningTransitionIntegrityError(
                        "conflicting COMPLETION evidence"
                    )
                continue
            completion = item

    if completion is not None and begin is None:
        raise StrategyGoverningTransitionIntegrityError(
            "COMPLETION evidence exists without BEGIN_EFFECTIVE"
        )

    if completion is not None:
        established = completion.established_target_state
        if (
            established is None
            or not _state_matches_context(established, authority.target_context)
        ):
            raise StrategyGoverningTransitionIntegrityError(
                "COMPLETION target durable state conflicts with target governing context"
            )
        return StrategyGoverningTransitionState.POST_TRANSITION

    if begin is not None:
        return StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS

    return StrategyGoverningTransitionState.PRE_TRANSITION


def evaluate_governing_transition(
    *,
    authority: StrategyGoverningTransitionAuthority,
    source_instance: StrategyInstance,
    durable_state: StrategyDurableStateReference,
    phase_evidence: tuple[StrategyGoverningTransitionPhaseEvidence, ...] = (),
) -> StrategyGoverningTransitionState:
    """驗證 exact C16 source authority 與 durable state；不授予 trading readiness。"""

    if authority.strategy_instance_id != source_instance.strategy_instance_id:
        raise StrategyGoverningTransitionIntegrityError(
            "transition authority conflicts with requested StrategyInstance"
        )

    if not _source_matches_instance(authority.source_context, source_instance):
        raise StrategyGoverningTransitionIntegrityError(
            "transition source governing context conflicts with C16 authority"
        )

    state = classify_governing_transition(
        authority=authority,
        phase_evidence=phase_evidence,
    )

    if state is StrategyGoverningTransitionState.PRE_TRANSITION:
        if not _state_matches_context(durable_state, authority.source_context):
            raise StrategyGoverningTransitionIntegrityError(
                "PRE_TRANSITION durable state does not match source governing context"
            )
        return state

    if state is StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS:
        if (
            not _state_matches_context(durable_state, authority.source_context)
            and not _state_matches_context(durable_state, authority.target_context)
        ):
            raise StrategyGoverningTransitionIntegrityError(
                "TRANSITION_IN_PROGRESS durable state matches neither governing context"
            )
        return state

    completion = next(
        item
        for item in phase_evidence
        if item.kind is StrategyGoverningTransitionPhaseKind.COMPLETION
    )
    established = completion.established_target_state
    if (
        established is None
        or durable_state != established
        or not _state_matches_context(durable_state, authority.target_context)
    ):
        raise StrategyGoverningTransitionIntegrityError(
            "POST_TRANSITION target-compatible durable state is missing or mismatched"
        )
    return state


class StrategyGoverningTransitionResolutionKind(str, Enum):
    """Current transition resolver 的 immutable resolution kinds。"""

    ACTIVE_TRANSITION = "ACTIVE_TRANSITION"
    NO_ACTIVE_TRANSITION = "NO_ACTIVE_TRANSITION"


class StrategyGoverningTransitionResolutionReceipt(BaseModel):
    """Resolver-produced immutable receipt；NO_ACTIVE 不是第四個 C17 state。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    resolution_id: str
    strategy_instance_id: str
    effective_governing_context: StrategyGoverningContext
    resolution_authority: StrategyAuthorityRef
    resolution_kind: StrategyGoverningTransitionResolutionKind
    transition_id: str | None = None
    resolution_revision: int = Field(ge=1)
    currentness_evidence_ref: str

    @field_validator(
        "resolution_id",
        "strategy_instance_id",
        "transition_id",
        "currentness_evidence_ref",
        mode="before",
    )
    @classmethod
    def _ids(cls, value: object) -> object:
        if value is None:
            return None
        return normalize_stable_id(value) if isinstance(value, str) else value

    @model_validator(mode="after")
    def _resolution_integrity(
        self,
    ) -> "StrategyGoverningTransitionResolutionReceipt":
        if (
            self.effective_governing_context.strategy_instance_id
            != self.strategy_instance_id
        ):
            raise ValueError(
                "transition resolution governing context conflicts with StrategyInstance"
            )

        expected = StrategyAuthorityRef(
            authority_id="STRATEGY-GOVERNING-TRANSITION-RESOLUTION",
            authority_version="V1",
        )
        if self.resolution_authority != expected:
            raise ValueError(
                "transition resolution authority identity/version mismatch"
            )

        active = (
            self.resolution_kind
            is StrategyGoverningTransitionResolutionKind.ACTIVE_TRANSITION
        )
        if active != (self.transition_id is not None):
            raise ValueError(
                "ACTIVE_TRANSITION requires transition_id and NO_ACTIVE_TRANSITION forbids it"
            )
        return self


class StrategyGoverningTransitionResolution(BaseModel):
    """Current CAS-head selected transition resolution + derived active phase。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    receipt: StrategyGoverningTransitionResolutionReceipt
    current_head_revision: int = Field(ge=1)
    transition_authority: StrategyGoverningTransitionAuthority | None = None
    phase_evidence: tuple[StrategyGoverningTransitionPhaseEvidence, ...] = ()

    @model_validator(mode="after")
    def _current_resolution(
        self,
    ) -> "StrategyGoverningTransitionResolution":
        if self.receipt.resolution_revision != self.current_head_revision:
            raise ValueError(
                "transition resolution receipt is stale against current CAS head"
            )

        if (
            self.receipt.resolution_kind
            is StrategyGoverningTransitionResolutionKind.NO_ACTIVE_TRANSITION
        ):
            if self.transition_authority is not None or self.phase_evidence:
                raise ValueError(
                    "NO_ACTIVE_TRANSITION cannot carry active transition material"
                )
            return self

        authority = self.transition_authority
        if authority is None:
            raise ValueError(
                "ACTIVE_TRANSITION requires exact transition descriptor"
            )
        if (
            authority.transition_id != self.receipt.transition_id
            or authority.strategy_instance_id != self.receipt.strategy_instance_id
        ):
            raise ValueError(
                "transition resolution does not bind exact active transition"
            )

        state = classify_governing_transition(
            authority=authority,
            phase_evidence=self.phase_evidence,
        )
        expected_context = (
            authority.target_context
            if state is StrategyGoverningTransitionState.POST_TRANSITION
            else authority.source_context
        )
        if self.receipt.effective_governing_context != expected_context:
            raise ValueError(
                "transition resolution effective governing context mismatch"
            )
        return self

    @property
    def transition_state(self) -> StrategyGoverningTransitionState | None:
        if (
            self.receipt.resolution_kind
            is StrategyGoverningTransitionResolutionKind.NO_ACTIVE_TRANSITION
        ):
            return None
        assert self.transition_authority is not None
        return classify_governing_transition(
            authority=self.transition_authority,
            phase_evidence=self.phase_evidence,
        )

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
                "K520 applicability instrument provenance conflicts with canonical instrument_id"
            )
        return self


def _k520_evidence_matches_context(
    *,
    evidence: K520ApplicabilityEvidence,
    context: StrategyGoverningContext,
) -> bool:
    return (
        evidence.strategy_instance_id == context.strategy_instance_id
        and evidence.strategy_id == context.strategy_id
        and evidence.config_version == context.config_version
        and evidence.config_fingerprint == context.config_fingerprint
        and evidence.implementation_revision == context.implementation_revision
        and evidence.instrument_id == context.instrument_id
        and evidence.instrument_binding_provenance
        == context.instrument_binding_provenance
        and evidence.timeframe == context.timeframe
    )


def _evaluate_k520_evidence_for_context(
    *,
    context: StrategyGoverningContext,
    evidence: K520ApplicabilityEvidence,
) -> K520ApplicabilityClassification:
    if not _k520_evidence_matches_context(
        evidence=evidence,
        context=context,
    ):
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


class K520ApplicabilityReceipt(BaseModel):
    """C19 trusted evaluated result；保留 exact governing world 與 proof material。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    receipt_id: str
    classification: K520ApplicabilityClassification
    governing_context: StrategyGoverningContext
    evidence: K520ApplicabilityEvidence

    @field_validator("receipt_id", mode="before")
    @classmethod
    def _receipt_id(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @model_validator(mode="after")
    def _receipt_integrity(self) -> "K520ApplicabilityReceipt":
        evaluated = _evaluate_k520_evidence_for_context(
            context=self.governing_context,
            evidence=self.evidence,
        )
        if self.classification is not evaluated:
            raise ValueError(
                "K520 receipt classification does not match exact governing-world evaluation"
            )
        return self


def evaluate_k520_applicability_receipt(
    *,
    governing_context: StrategyGoverningContext,
    evidence: K520ApplicabilityEvidence,
) -> K520ApplicabilityReceipt:
    """C19 trusted path：針對 C17 effective governing context 產生 receipt。"""

    return K520ApplicabilityReceipt(
        receipt_id=evidence.evidence_id,
        classification=_evaluate_k520_evidence_for_context(
            context=governing_context,
            evidence=evidence,
        ),
        governing_context=governing_context,
        evidence=evidence,
    )


def evaluate_k520_applicability(
    *,
    instance: StrategyInstance,
    evidence: K520ApplicabilityEvidence,
) -> K520ApplicabilityClassification:
    """Compatibility projection；C18 trusted path 不得以裸 enum 取代 receipt。"""

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

    # 使用同一完整 proof 規則保留既有 API。
    context = StrategyGoverningContext(
        strategy_instance_id=instance.strategy_instance_id,
        strategy_id=instance.strategy_id,
        config_authority=StrategyAuthorityRef(
            authority_id="LEGACY-C16-COMPATIBILITY",
            authority_version=instance.config_version,
        ),
        config_version=instance.config_version,
        config_fingerprint=instance.config_fingerprint,
        implementation_revision=instance.implementation_revision,
        instrument_id=instance.instrument_id,
        instrument_binding_provenance=provenance,
        timeframe=instance.timeframe,
        state_schema_reference=StrategyStateSchemaReference(
            strategy_id=instance.strategy_id,
            schema_version=1,
        ),
    )
    # config_authority/schema are not part of K520 evidence binding; other exact
    # governing fields are re-used by the common evaluator.
    return _evaluate_k520_evidence_for_context(
        context=context,
        evidence=evidence,
    )

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
    """C20 completeness gate readiness；不代表 StrategyTradingReady。"""

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
    """C20 approved completeness/currentness evidence；不實作 detector/service。"""

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
    """Compatibility projection；trusted C18 path consumes receipt。"""

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


def _trusted_completeness_readiness(
    *,
    requirement: CompletenessRequirementAuthority | None,
    evidence: CompletenessEvidenceAuthority | None,
    runtime_authority_class: CompletenessAuthorityClass,
) -> CompletenessReadiness:
    """Strategy readiness receipt 必須有 exact current-world evidence。"""

    if requirement is None or evidence is None:
        return CompletenessReadiness.NOT_READY
    if (
        requirement.authority_class is not runtime_authority_class
        or evidence.authority_class is not runtime_authority_class
    ):
        return CompletenessReadiness.NOT_READY
    if (
        requirement.classification
        is CompletenessRequirementClassification.UNKNOWN
    ):
        return CompletenessReadiness.NOT_READY
    if not (
        evidence.consumer_ref == requirement.consumer_ref
        and evidence.scope_ref == requirement.scope_ref
        and evidence.stream_ref == requirement.stream_ref
        and evidence.horizon_ref == requirement.horizon_ref
        and evidence.policy_authority == requirement.policy_authority
        and evidence.authority_class == requirement.authority_class
    ):
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


class CompletenessReadinessReceipt(BaseModel):
    """C20 trusted evaluated result；保留 requirement/evidence/current world。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    receipt_id: str
    readiness: CompletenessReadiness
    governing_context: StrategyGoverningContext
    runtime_authority_class: CompletenessAuthorityClass
    requirement: CompletenessRequirementAuthority | None
    evidence: CompletenessEvidenceAuthority | None

    @field_validator("receipt_id", mode="before")
    @classmethod
    def _receipt_id(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @model_validator(mode="after")
    def _receipt_integrity(self) -> "CompletenessReadinessReceipt":
        expected = _trusted_completeness_readiness(
            requirement=self.requirement,
            evidence=self.evidence,
            runtime_authority_class=self.runtime_authority_class,
        )
        if self.readiness is not expected:
            raise ValueError(
                "completeness receipt readiness does not match exact authority/current-world evaluation"
            )
        return self


def evaluate_completeness_readiness_receipt(
    *,
    governing_context: StrategyGoverningContext,
    requirement: CompletenessRequirementAuthority | None,
    evidence: CompletenessEvidenceAuthority | None,
    runtime_authority_class: CompletenessAuthorityClass,
) -> CompletenessReadinessReceipt:
    """C20 trusted receipt；保留 consumer/scope/policy/environment/world。"""

    receipt_id = (
        evidence.evidence_id
        if evidence is not None
        else requirement.requirement_id
        if requirement is not None
        else "C20-MISSING-AUTHORITY"
    )
    return CompletenessReadinessReceipt(
        receipt_id=receipt_id,
        readiness=_trusted_completeness_readiness(
            requirement=requirement,
            evidence=evidence,
            runtime_authority_class=runtime_authority_class,
        ),
        governing_context=governing_context,
        runtime_authority_class=runtime_authority_class,
        requirement=requirement,
        evidence=evidence,
    )

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
        if self.governing_context.strategy_instance_id != self.strategy_instance_id:
            raise ValueError(
                "restore evidence conflicts with StrategyInstance identity"
            )
        return self


class K520RecoveryEvidenceRef(BaseModel):
    """C18 僅消費 approved K520/GAP-09 evidence reference；不實作 K520。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_ref: str
    strategy_instance_id: str
    strategy_id: str
    config_version: str
    config_fingerprint: str
    implementation_revision: str
    instrument_id: int = Field(gt=0)
    instrument_binding_provenance: CanonicalInstrumentBindingProvenance
    timeframe: str
    authority: StrategyAuthorityRef
    ready: bool

    @field_validator(
        "evidence_ref",
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


class StrategyTradingReadinessEvaluation(BaseModel):
    """四層 readiness 中的 StrategyRestoreValid / StrategyTradingReady projection。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    strategy_instance_id: str
    broker_account_execution_ready: bool
    strategy_restore_valid: bool
    strategy_trading_ready: bool
    decision_policy_version: str | None = None
    reasons: tuple[str, ...] = ()

    @field_validator("strategy_instance_id", mode="before")
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

    @field_validator("policy_id", "policy_version", mode="before")
    @classmethod
    def _stable_ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value


class RequiredCohortMembershipEvidence(BaseModel):
    """Provider-resolved membership；caller object 本身不是 production trust boundary。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    evidence_id: str
    cohort_id: str
    policy: DecisionPolicyAuthorityRef
    required_strategy_instance_ids: tuple[str, ...]
    membership_authority: StrategyAuthorityRef
    evaluated_policy_currentness_ref: str
    current_policy_currentness_ref: str
    evaluated_membership_currentness_ref: str
    current_membership_currentness_ref: str

    @field_validator(
        "evidence_id",
        "cohort_id",
        "evaluated_policy_currentness_ref",
        "current_policy_currentness_ref",
        "evaluated_membership_currentness_ref",
        "current_membership_currentness_ref",
        mode="before",
    )
    @classmethod
    def _stable_ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("required_strategy_instance_ids", mode="before")
    @classmethod
    def _required_ids(cls, value: object) -> object:
        if isinstance(value, (tuple, list)):
            return tuple(normalize_stable_id(item) for item in value)
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

    @property
    def current(self) -> bool:
        return (
            self.evaluated_policy_currentness_ref
            == self.current_policy_currentness_ref
            and self.evaluated_membership_currentness_ref
            == self.current_membership_currentness_ref
        )


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

    @field_validator("cohort_id", "decision_policy_version", mode="before")
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


def _k520_recovery_evidence_matches_context(
    *,
    evidence: K520RecoveryEvidenceRef,
    context: StrategyGoverningContext,
) -> bool:
    return (
        evidence.strategy_instance_id == context.strategy_instance_id
        and evidence.strategy_id == context.strategy_id
        and evidence.config_version == context.config_version
        and evidence.config_fingerprint == context.config_fingerprint
        and evidence.implementation_revision == context.implementation_revision
        and evidence.instrument_id == context.instrument_id
        and evidence.instrument_binding_provenance
        == context.instrument_binding_provenance
        and evidence.timeframe == context.timeframe
    )


def evaluate_strategy_trading_readiness(
    *,
    instance: StrategyInstance,
    broker_account: BrokerAccountExecutionReadyInput,
    restore: StrategyRestoreValidEvidence,
    transition_resolution: StrategyGoverningTransitionResolution | None,
    k520_receipt: K520ApplicabilityReceipt | None,
    k520_evidence: K520RecoveryEvidenceRef | None,
    completeness_receipt: CompletenessReadinessReceipt | None,
    runtime_completeness_authority_class: CompletenessAuthorityClass,
) -> StrategyTradingReadinessEvaluation:
    """C18 trusted strategy readiness；缺少 exact resolver/receipt 一律 fail closed。"""

    reasons: list[str] = []

    if not broker_account.ready:
        reasons.append("BrokerAccountExecutionReady is false")

    if not restore.valid:
        reasons.append("StrategyRestoreValid is false")

    effective_context = restore.governing_context

    if transition_resolution is None:
        reasons.append(
            "governing transition resolution authority is missing or unresolved"
        )
    else:
        receipt = transition_resolution.receipt
        effective_context = receipt.effective_governing_context

        if receipt.strategy_instance_id != instance.strategy_instance_id:
            reasons.append(
                "transition resolution StrategyInstance identity mismatch"
            )

        if (
            receipt.resolution_kind
            is StrategyGoverningTransitionResolutionKind.ACTIVE_TRANSITION
        ):
            authority = transition_resolution.transition_authority
            if authority is None:
                reasons.append("active transition descriptor is missing")
            else:
                if not _source_matches_instance(
                    authority.source_context,
                    instance,
                ):
                    reasons.append(
                        "active transition source context conflicts with C16 authority"
                    )

                state = transition_resolution.transition_state
                if (
                    state
                    is StrategyGoverningTransitionState.TRANSITION_IN_PROGRESS
                ):
                    reasons.append("governing transition is in progress")
                elif (
                    state is StrategyGoverningTransitionState.PRE_TRANSITION
                    and effective_context != authority.source_context
                ):
                    reasons.append(
                        "PRE_TRANSITION resolution does not bind exact source context"
                    )
                elif (
                    state is StrategyGoverningTransitionState.POST_TRANSITION
                    and effective_context != authority.target_context
                ):
                    reasons.append(
                        "POST_TRANSITION resolution does not bind exact target context"
                    )

    if not _context_matches_restore(
        context=effective_context,
        restore=restore,
    ):
        reasons.append(
            "restore evidence does not bind exact effective governing context"
        )

    if k520_receipt is None:
        reasons.append("C19 governing-world receipt is missing")
    elif k520_receipt.governing_context != effective_context:
        reasons.append(
            "C19 receipt does not bind exact effective governing context"
        )
    elif (
        k520_receipt.classification
        is K520ApplicabilityClassification.UNKNOWN
    ):
        reasons.append("K520 applicability is unknown")
    elif (
        k520_receipt.classification
        is K520ApplicabilityClassification.REQUIRED
    ):
        if (
            k520_evidence is None
            or not k520_evidence.ready
            or not _k520_recovery_evidence_matches_context(
                evidence=k520_evidence,
                context=effective_context,
            )
        ):
            reasons.append(
                "required K520 recovery evidence is missing, not ready, or mismatched"
            )

    if completeness_receipt is None:
        reasons.append("C20 governing-world readiness receipt is missing")
    else:
        requirement = completeness_receipt.requirement
        evidence = completeness_receipt.evidence
        expected_consumer = (
            f"STRATEGY-INSTANCE:{effective_context.strategy_instance_id}"
        )
        expected_scope = (
            f"INSTRUMENT:{effective_context.instrument_id}"
            f"/TIMEFRAME:{effective_context.timeframe}"
        )

        if completeness_receipt.governing_context != effective_context:
            reasons.append(
                "C20 receipt does not bind exact effective governing context"
            )
        if (
            completeness_receipt.runtime_authority_class
            is not runtime_completeness_authority_class
        ):
            reasons.append(
                "C20 receipt authority class does not match runtime environment"
            )
        if completeness_receipt.readiness is not CompletenessReadiness.READY:
            reasons.append("completeness dependency is not ready")
        if requirement is None or evidence is None:
            reasons.append(
                "C20 receipt lacks exact requirement/current-world authority"
            )
        else:
            if (
                requirement.consumer_ref != expected_consumer
                or requirement.scope_ref != expected_scope
                or evidence.consumer_ref != expected_consumer
                or evidence.scope_ref != expected_scope
            ):
                reasons.append(
                    "C20 receipt consumer/scope does not match current Strategy"
                )
            if (
                evidence.stream_ref != requirement.stream_ref
                or evidence.horizon_ref != requirement.horizon_ref
                or evidence.policy_authority != requirement.policy_authority
            ):
                reasons.append(
                    "C20 receipt stream/horizon/policy authority mismatch"
                )
            if (
                evidence.evaluated_world_ref != evidence.current_world_ref
                or evidence.evaluated_frontier_revision_id
                != evidence.current_frontier_revision_id
            ):
                reasons.append(
                    "C20 receipt world/frontier currentness mismatch"
                )

    ready = not reasons

    return StrategyTradingReadinessEvaluation(
        strategy_instance_id=instance.strategy_instance_id,
        broker_account_execution_ready=broker_account.ready,
        strategy_restore_valid=restore.valid,
        strategy_trading_ready=ready,
        decision_policy_version=effective_context.decision_policy_version,
        reasons=tuple(reasons),
    )


def evaluate_decision_cohort_trading_readiness(
    *,
    membership: RequiredCohortMembershipEvidence | None,
    strategy_readiness: tuple[StrategyTradingReadinessEvaluation, ...],
    runtime_authority_class: DecisionPolicyAuthorityClass,
) -> DecisionCohortTradingReadinessEvaluation:
    """Pure composition primitive；production trust boundary must resolve membership itself。"""

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
            required_strategy_instance_ids=membership.required_strategy_instance_ids,
            reasons=(
                "DecisionPolicy authority class does not match runtime environment",
            ),
        )

    if not membership.current:
        return DecisionCohortTradingReadinessEvaluation(
            cohort_id=membership.cohort_id,
            decision_policy_version=membership.policy.policy_version,
            decision_cohort_trading_ready=False,
            required_strategy_instance_ids=membership.required_strategy_instance_ids,
            reasons=("DecisionPolicy/cohort membership authority is stale",),
        )

    by_id: dict[str, StrategyTradingReadinessEvaluation] = {}
    for item in strategy_readiness:
        if item.strategy_instance_id in by_id:
            raise ValueError(
                "duplicate StrategyInstance readiness cannot define cohort membership"
            )
        by_id[item.strategy_instance_id] = item

    required = membership.required_strategy_instance_ids
    missing = tuple(item for item in required if item not in by_id)
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
    "CompletenessEvidenceAuthority",
    "CompletenessReadiness",
    "CompletenessReadinessReceipt",
    "CompletenessRequirementAuthority",
    "CompletenessRequirementClassification",
    "DecisionCohortTradingReadinessEvaluation",
    "DecisionPolicyAuthorityClass",
    "DecisionPolicyAuthorityRef",
    "K520ApplicabilityClassification",
    "K520ApplicabilityEvidence",
    "K520ApplicabilityReceipt",
    "K520RecoveryEvidenceRef",
    "RequiredCohortMembershipEvidence",
    "StartupCatchUpIsolationEvaluation",
    "StartupCatchUpOutputKind",
    "StrategyAuthorityRef",
    "StrategyDurableStateReference",
    "StrategyGoverningContext",
    "StrategyGoverningTransitionAuthority",
    "StrategyGoverningTransitionIntegrityError",
    "StrategyGoverningTransitionPhaseEvidence",
    "StrategyGoverningTransitionPhaseKind",
    "StrategyGoverningTransitionResolution",
    "StrategyGoverningTransitionResolutionKind",
    "StrategyGoverningTransitionResolutionReceipt",
    "StrategyGoverningTransitionState",
    "StrategyRestoreValidEvidence",
    "StrategyStateSchemaReference",
    "StrategyTradingReadinessEvaluation",
    "classify_governing_transition",
    "evaluate_completeness_readiness",
    "evaluate_completeness_readiness_receipt",
    "evaluate_decision_cohort_trading_readiness",
    "evaluate_generic_startup_catch_up_output",
    "evaluate_governing_transition",
    "evaluate_k520_applicability",
    "evaluate_k520_applicability_receipt",
    "evaluate_strategy_trading_readiness",
]
