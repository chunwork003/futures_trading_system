from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol, runtime_checkable

from domain.market_observation import MarketObservationRevisionId
from domain.market_observation_acceptance import (
    MarketObservationAcceptancePolicy,
    MarketObservationCandidateEvidence,
    MarketObservationDecisionKind,
    MarketObservationRevision,
)
from persistence.contracts import PersistenceConflictError


class MarketObservationPersistenceError(RuntimeError):
    """C24 operational market-observation persistence failure。"""


class MarketObservationIdentityConflictError(PersistenceConflictError):
    """同一 mor1 revision identity 對應不同 structured canonical evidence。"""


class MarketObservationCandidateConflictError(PersistenceConflictError):
    """同一 candidate_id 對應不同 immutable candidate evidence。"""


class MarketObservationPolicyConflictError(PersistenceConflictError):
    """同一 policy identity/version 對應不同 immutable policy evidence。"""


class MarketObservationDecisionConflictError(PersistenceConflictError):
    """同一 decision_id 對應不同 immutable decision evidence。"""


def _stable_id(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{field_name} must not be blank")

    return normalized


def _aware_utc(value: object, field_name: str) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError(
            f"{field_name} must be timezone-aware"
        )

    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class MarketObservationCandidateDecisionEvidence:
    """不可變 candidate acceptance/quarantine audit evidence。"""

    decision_id: str
    candidate_id: str
    decision_kind: MarketObservationDecisionKind
    decided_at: datetime
    linked_revision_id: MarketObservationRevisionId | None
    reason: str | None
    acceptance_policy_id: str
    acceptance_policy_version: int
    acceptance_scope_ref: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "decision_id",
            _stable_id(self.decision_id, "decision_id"),
        )
        object.__setattr__(
            self,
            "candidate_id",
            _stable_id(self.candidate_id, "candidate_id"),
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
        object.__setattr__(
            self,
            "decided_at",
            _aware_utc(self.decided_at, "decided_at"),
        )

        if (
            type(self.acceptance_policy_version) is not int
            or self.acceptance_policy_version < 1
        ):
            raise ValueError(
                "acceptance_policy_version must be positive"
            )

        if self.reason is not None:
            object.__setattr__(
                self,
                "reason",
                _stable_id(self.reason, "reason"),
            )


@dataclass(frozen=True, slots=True)
class MarketObservationAcceptanceResult:
    """Caller-owned UoW 內完成 C24 evidence mutation 後的 deterministic result。"""

    decision: MarketObservationCandidateDecisionEvidence
    accepted_revision: MarketObservationRevision | None
    current_revision_id: MarketObservationRevisionId | None
    current_revision_seq: int
    quarantined: bool
    integrity_error: PersistenceConflictError | None = None

    def __post_init__(self) -> None:
        if (
            type(self.current_revision_seq) is not int
            or self.current_revision_seq < 0
        ):
            raise ValueError(
                "current_revision_seq must be non-negative"
            )


@runtime_checkable
class MarketObservationAcceptanceRepository(Protocol):
    """C24 storage-neutral port；transaction authority 由 caller UoW 持有。"""

    def append_policy(
        self,
        policy: MarketObservationAcceptancePolicy,
    ) -> bool:
        ...

    def process_candidate(
        self,
        *,
        policy: MarketObservationAcceptancePolicy,
        candidate: MarketObservationCandidateEvidence,
        decision_id: str,
        decided_at: datetime,
    ) -> MarketObservationAcceptanceResult:
        ...


__all__ = [
    "MarketObservationAcceptanceRepository",
    "MarketObservationAcceptanceResult",
    "MarketObservationCandidateConflictError",
    "MarketObservationCandidateDecisionEvidence",
    "MarketObservationDecisionConflictError",
    "MarketObservationIdentityConflictError",
    "MarketObservationPersistenceError",
    "MarketObservationPolicyConflictError",
]
