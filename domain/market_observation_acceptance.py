from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from domain.market_observation import (
    CanonicalMarketObservationContent,
    MarketObservationContentFingerprint,
    MarketObservationLogicalKey,
    MarketObservationRevisionId,
    build_market_observation_revision_id,
)


class MarketObservationAcceptanceContractError(ValueError):
    """市場觀測 acceptance/policy evidence 違反已凍結的 C24 contract。"""


def _stable_id(value: object, field_name: str) -> str:
    """所有 authority/evidence ID 必須由上游明確提供，禁止隱式生成。"""

    if not isinstance(value, str):
        raise MarketObservationAcceptanceContractError(
            f"{field_name} must be a string"
        )

    normalized = value.strip()

    if not normalized:
        raise MarketObservationAcceptanceContractError(
            f"{field_name} must not be blank"
        )

    return normalized


def _optional_stable_id(
    value: object | None,
    field_name: str,
) -> str | None:
    if value is None:
        return None
    return _stable_id(value, field_name)


def _aware_utc(value: object, field_name: str) -> datetime:
    """接受事件時間必須顯式具時區；不得使用 local-now fallback。"""

    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise MarketObservationAcceptanceContractError(
            f"{field_name} must be timezone-aware"
        )

    return value.astimezone(timezone.utc)


class MarketObservationRoutingRole(str, Enum):
    """資料 routing preference；絕不等同 canonical truth authority。"""

    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    VALIDATION = "VALIDATION"


class MarketObservationDecisionKind(str, Enum):
    """C24 operational acceptance/quarantine decision evidence。"""

    ACCEPTED_NEW_REVISION = "ACCEPTED_NEW_REVISION"
    CORROBORATED_EXISTING = "CORROBORATED_EXISTING"
    QUARANTINED_INELIGIBLE_SOURCE = "QUARANTINED_INELIGIBLE_SOURCE"
    QUARANTINED_UNPROVEN_CORRECTION = "QUARANTINED_UNPROVEN_CORRECTION"
    QUARANTINED_CROSS_SOURCE_CONFLICT = "QUARANTINED_CROSS_SOURCE_CONFLICT"
    IDENTITY_CONFLICT = "IDENTITY_CONFLICT"


@dataclass(frozen=True, slots=True)
class MarketObservationSourcePolicyRule:
    """單一 source 在某 policy scope 中的明確 truth/correction 權限。"""

    source_id: str
    evidence_eligible: bool
    can_seed_initial_truth: bool
    authoritative_for_scope: bool
    can_accept_formal_correction: bool

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "source_id",
            _stable_id(self.source_id, "source_id"),
        )

        for field_name in (
            "evidence_eligible",
            "can_seed_initial_truth",
            "authoritative_for_scope",
            "can_accept_formal_correction",
        ):
            if type(getattr(self, field_name)) is not bool:
                raise MarketObservationAcceptanceContractError(
                    f"{field_name} must be bool"
                )


@dataclass(frozen=True, slots=True)
class MarketObservationAcceptancePolicy:
    """Versioned immutable truth-selection policy；不進入 mor1 identity。"""

    policy_id: str
    version: int
    scope_ref: str
    source_rules: tuple[MarketObservationSourcePolicyRule, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "policy_id",
            _stable_id(self.policy_id, "policy_id"),
        )
        object.__setattr__(
            self,
            "scope_ref",
            _stable_id(self.scope_ref, "scope_ref"),
        )

        if type(self.version) is not int or self.version < 1:
            raise MarketObservationAcceptanceContractError(
                "policy version must be a positive integer"
            )

        normalized_rules = tuple(self.source_rules)

        if not normalized_rules:
            raise MarketObservationAcceptanceContractError(
                "source_rules must not be empty"
            )

        if not all(
            isinstance(rule, MarketObservationSourcePolicyRule)
            for rule in normalized_rules
        ):
            raise MarketObservationAcceptanceContractError(
                "source_rules must contain MarketObservationSourcePolicyRule"
            )

        source_ids = [
            rule.source_id
            for rule in normalized_rules
        ]

        if len(source_ids) != len(set(source_ids)):
            raise MarketObservationAcceptanceContractError(
                "source_rules must not contain duplicate source_id"
            )

        object.__setattr__(
            self,
            "source_rules",
            normalized_rules,
        )

    def rule_for(
        self,
        source_id: str,
    ) -> MarketObservationSourcePolicyRule | None:
        normalized = _stable_id(source_id, "source_id")

        for rule in self.source_rules:
            if rule.source_id == normalized:
                return rule

        return None


@dataclass(frozen=True, slots=True)
class MarketObservationCandidateEvidence:
    """不可變 candidate/provenance evidence；持久化不代表已接受。"""

    candidate_id: str
    logical_key: MarketObservationLogicalKey
    content: CanonicalMarketObservationContent
    content_fingerprint: MarketObservationContentFingerprint
    observation_revision_id: MarketObservationRevisionId
    source_id: str
    routing_role: MarketObservationRoutingRole
    source_record_ref: str | None
    formal_correction_ref: str | None
    received_at: datetime
    provenance_json: Mapping[str, object]
    acceptance_policy_id: str
    acceptance_policy_version: int
    acceptance_scope_ref: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "candidate_id",
            _stable_id(self.candidate_id, "candidate_id"),
        )
        object.__setattr__(
            self,
            "source_id",
            _stable_id(self.source_id, "source_id"),
        )
        object.__setattr__(
            self,
            "source_record_ref",
            _optional_stable_id(
                self.source_record_ref,
                "source_record_ref",
            ),
        )
        object.__setattr__(
            self,
            "formal_correction_ref",
            _optional_stable_id(
                self.formal_correction_ref,
                "formal_correction_ref",
            ),
        )
        object.__setattr__(
            self,
            "acceptance_policy_id",
            _stable_id(
                self.acceptance_policy_id,
                "acceptance_policy_id",
            ),
        )
        object.__setattr__(
            self,
            "acceptance_scope_ref",
            _stable_id(
                self.acceptance_scope_ref,
                "acceptance_scope_ref",
            ),
        )

        if type(self.acceptance_policy_version) is not int:
            raise MarketObservationAcceptanceContractError(
                "acceptance_policy_version must be integer"
            )

        if self.acceptance_policy_version < 1:
            raise MarketObservationAcceptanceContractError(
                "acceptance_policy_version must be positive"
            )

        if not isinstance(
            self.routing_role,
            MarketObservationRoutingRole,
        ):
            raise MarketObservationAcceptanceContractError(
                "routing_role must be MarketObservationRoutingRole"
            )

        object.__setattr__(
            self,
            "received_at",
            _aware_utc(self.received_at, "received_at"),
        )

        if not isinstance(self.provenance_json, Mapping):
            raise MarketObservationAcceptanceContractError(
                "provenance_json must be a mapping"
            )

        object.__setattr__(
            self,
            "provenance_json",
            MappingProxyType(dict(self.provenance_json)),
        )

        expected_fingerprint = self.content.content_fingerprint

        if self.content_fingerprint != expected_fingerprint:
            raise MarketObservationAcceptanceContractError(
                "candidate content_fingerprint does not match canonical content"
            )

        expected_revision_id = build_market_observation_revision_id(
            logical_key=self.logical_key,
            content_fingerprint=self.content_fingerprint,
        )

        if self.observation_revision_id != expected_revision_id:
            raise MarketObservationAcceptanceContractError(
                "candidate observation_revision_id does not match canonical identity"
            )


@dataclass(frozen=True, slots=True)
class MarketObservationRevision:
    """已接受 canonical revision；revision_seq 為 logical-key authority order。"""

    observation_revision_id: MarketObservationRevisionId
    logical_key: MarketObservationLogicalKey
    content: CanonicalMarketObservationContent
    content_fingerprint: MarketObservationContentFingerprint
    revision_seq: int
    supersedes_revision_id: MarketObservationRevisionId | None
    accepted_at: datetime
    acceptance_policy_id: str
    acceptance_policy_version: int
    acceptance_scope_ref: str

    def __post_init__(self) -> None:
        if type(self.revision_seq) is not int or self.revision_seq < 1:
            raise MarketObservationAcceptanceContractError(
                "revision_seq must be a positive integer"
            )

        if self.revision_seq == 1:
            if self.supersedes_revision_id is not None:
                raise MarketObservationAcceptanceContractError(
                    "revision_seq 1 must not supersede another revision"
                )
        elif self.supersedes_revision_id is None:
            raise MarketObservationAcceptanceContractError(
                "revision_seq > 1 requires supersedes_revision_id"
            )

        object.__setattr__(
            self,
            "accepted_at",
            _aware_utc(self.accepted_at, "accepted_at"),
        )
        object.__setattr__(
            self,
            "acceptance_policy_id",
            _stable_id(
                self.acceptance_policy_id,
                "acceptance_policy_id",
            ),
        )
        object.__setattr__(
            self,
            "acceptance_scope_ref",
            _stable_id(
                self.acceptance_scope_ref,
                "acceptance_scope_ref",
            ),
        )

        if (
            type(self.acceptance_policy_version) is not int
            or self.acceptance_policy_version < 1
        ):
            raise MarketObservationAcceptanceContractError(
                "acceptance_policy_version must be positive"
            )

        if self.content_fingerprint != self.content.content_fingerprint:
            raise MarketObservationAcceptanceContractError(
                "revision content fingerprint mismatch"
            )

        expected_revision_id = build_market_observation_revision_id(
            logical_key=self.logical_key,
            content_fingerprint=self.content_fingerprint,
        )

        if self.observation_revision_id != expected_revision_id:
            raise MarketObservationAcceptanceContractError(
                "accepted revision ID does not match canonical identity"
            )


@dataclass(frozen=True, slots=True)
class MarketObservationAcceptancePlan:
    """純 domain acceptance 結果；不執行 persistence 或 side effect。"""

    decision_kind: MarketObservationDecisionKind
    accepted_revision: MarketObservationRevision | None
    linked_revision_id: MarketObservationRevisionId | None
    quarantine_reason: str | None

    @property
    def quarantined(self) -> bool:
        return self.decision_kind in {
            MarketObservationDecisionKind.QUARANTINED_INELIGIBLE_SOURCE,
            MarketObservationDecisionKind.QUARANTINED_UNPROVEN_CORRECTION,
            MarketObservationDecisionKind.QUARANTINED_CROSS_SOURCE_CONFLICT,
            MarketObservationDecisionKind.IDENTITY_CONFLICT,
        }


def _validate_policy_binding(
    *,
    policy: MarketObservationAcceptancePolicy,
    candidate: MarketObservationCandidateEvidence,
) -> None:
    if candidate.acceptance_policy_id != policy.policy_id:
        raise MarketObservationAcceptanceContractError(
            "candidate acceptance_policy_id does not match policy"
        )

    if candidate.acceptance_policy_version != policy.version:
        raise MarketObservationAcceptanceContractError(
            "candidate acceptance_policy_version does not match policy"
        )

    if candidate.acceptance_scope_ref != policy.scope_ref:
        raise MarketObservationAcceptanceContractError(
            "candidate acceptance scope does not match policy"
        )


def evaluate_market_observation_candidate(
    *,
    policy: MarketObservationAcceptancePolicy,
    candidate: MarketObservationCandidateEvidence,
    current_revision: MarketObservationRevision | None,
    accepted_at: datetime,
) -> MarketObservationAcceptancePlan:
    """以顯式 policy/evidence 評估 candidate；arrival order 不具 truth authority。"""

    _validate_policy_binding(
        policy=policy,
        candidate=candidate,
    )

    normalized_accepted_at = _aware_utc(
        accepted_at,
        "accepted_at",
    )

    rule = policy.rule_for(candidate.source_id)

    if rule is None or not rule.evidence_eligible:
        return MarketObservationAcceptancePlan(
            decision_kind=(
                MarketObservationDecisionKind
                .QUARANTINED_INELIGIBLE_SOURCE
            ),
            accepted_revision=None,
            linked_revision_id=(
                None
                if current_revision is None
                else current_revision.observation_revision_id
            ),
            quarantine_reason="SOURCE_NOT_EVIDENCE_ELIGIBLE",
        )

    if current_revision is None:
        if not rule.can_seed_initial_truth:
            return MarketObservationAcceptancePlan(
                decision_kind=(
                    MarketObservationDecisionKind
                    .QUARANTINED_INELIGIBLE_SOURCE
                ),
                accepted_revision=None,
                linked_revision_id=None,
                quarantine_reason="SOURCE_CANNOT_SEED_INITIAL_TRUTH",
            )

        accepted_revision = MarketObservationRevision(
            observation_revision_id=candidate.observation_revision_id,
            logical_key=candidate.logical_key,
            content=candidate.content,
            content_fingerprint=candidate.content_fingerprint,
            revision_seq=1,
            supersedes_revision_id=None,
            accepted_at=normalized_accepted_at,
            acceptance_policy_id=policy.policy_id,
            acceptance_policy_version=policy.version,
            acceptance_scope_ref=policy.scope_ref,
        )

        return MarketObservationAcceptancePlan(
            decision_kind=(
                MarketObservationDecisionKind.ACCEPTED_NEW_REVISION
            ),
            accepted_revision=accepted_revision,
            linked_revision_id=accepted_revision.observation_revision_id,
            quarantine_reason=None,
        )

    if current_revision.logical_key != candidate.logical_key:
        raise MarketObservationAcceptanceContractError(
            "current revision logical key does not match candidate"
        )

    if (
        current_revision.content_fingerprint
        == candidate.content_fingerprint
    ):
        if (
            current_revision.observation_revision_id
            != candidate.observation_revision_id
        ):
            raise MarketObservationAcceptanceContractError(
                "same canonical content must resolve to the same revision ID"
            )

        return MarketObservationAcceptancePlan(
            decision_kind=(
                MarketObservationDecisionKind.CORROBORATED_EXISTING
            ),
            accepted_revision=None,
            linked_revision_id=current_revision.observation_revision_id,
            quarantine_reason=None,
        )

    if (
        rule.can_accept_formal_correction
        and candidate.formal_correction_ref is not None
    ):
        accepted_revision = MarketObservationRevision(
            observation_revision_id=candidate.observation_revision_id,
            logical_key=candidate.logical_key,
            content=candidate.content,
            content_fingerprint=candidate.content_fingerprint,
            revision_seq=current_revision.revision_seq + 1,
            supersedes_revision_id=(
                current_revision.observation_revision_id
            ),
            accepted_at=normalized_accepted_at,
            acceptance_policy_id=policy.policy_id,
            acceptance_policy_version=policy.version,
            acceptance_scope_ref=policy.scope_ref,
        )

        return MarketObservationAcceptancePlan(
            decision_kind=(
                MarketObservationDecisionKind.ACCEPTED_NEW_REVISION
            ),
            accepted_revision=accepted_revision,
            linked_revision_id=accepted_revision.observation_revision_id,
            quarantine_reason=None,
        )

    decision_kind = (
        MarketObservationDecisionKind.QUARANTINED_CROSS_SOURCE_CONFLICT
        if candidate.routing_role
        is MarketObservationRoutingRole.VALIDATION
        else MarketObservationDecisionKind.QUARANTINED_UNPROVEN_CORRECTION
    )

    return MarketObservationAcceptancePlan(
        decision_kind=decision_kind,
        accepted_revision=None,
        linked_revision_id=current_revision.observation_revision_id,
        quarantine_reason="DIFFERENT_CONTENT_WITHOUT_FORMAL_CORRECTION_PROOF",
    )


__all__ = [
    "MarketObservationAcceptanceContractError",
    "MarketObservationAcceptancePlan",
    "MarketObservationAcceptancePolicy",
    "MarketObservationCandidateEvidence",
    "MarketObservationDecisionKind",
    "MarketObservationRevision",
    "MarketObservationRoutingRole",
    "MarketObservationSourcePolicyRule",
    "evaluate_market_observation_candidate",
]
