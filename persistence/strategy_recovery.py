from __future__ import annotations

from typing import Protocol, runtime_checkable

from strategy.recovery import (
    RequiredCohortMembershipEvidence,
    StrategyGoverningTransitionAuthority,
)


class StrategyTransitionPersistenceIntegrityError(ValueError):
    """Durable C17 transition authority identity/material 不一致。"""


class StrategyTransitionHeadConflictError(RuntimeError):
    """C17 current-head CAS 或 exact pointer authority 發生衝突。"""


@runtime_checkable
class StrategyGoverningTransitionRepository(Protocol):
    """C17 append-only authority + exact current-head pointer persistence port。"""

    def append(
        self,
        authority: StrategyGoverningTransitionAuthority,
    ) -> None:
        ...

    def advance_head(
        self,
        *,
        strategy_instance_id: str,
        transition_id: str,
        expected_head_revision: int,
    ) -> int:
        ...

    def current(
        self,
        strategy_instance_id: str,
    ) -> StrategyGoverningTransitionAuthority | None:
        ...



@runtime_checkable
class DecisionCohortAuthorityProvider(Protocol):
    """G / Decision Domain authority 的 C18 consumer-facing provider seam。"""

    def resolve_required_membership(
        self,
        *,
        cohort_id: str,
        policy_version: str,
    ) -> RequiredCohortMembershipEvidence | None:
        ...

__all__ = [
    "DecisionCohortAuthorityProvider",
    "StrategyGoverningTransitionRepository",
    "StrategyTransitionHeadConflictError",
    "StrategyTransitionPersistenceIntegrityError",
]
