from __future__ import annotations

from typing import Protocol, runtime_checkable

from strategy.recovery import (
    DecisionPolicyAuthorityRef,
    RequiredCohortMembershipEvidence,
    StrategyGoverningTransitionAuthority,
    StrategyGoverningTransitionPhaseEvidence,
    StrategyGoverningTransitionResolution,
    StrategyGoverningTransitionResolutionReceipt,
)


class StrategyTransitionPersistenceIntegrityError(ValueError):
    """Durable C17 descriptor/evidence/resolution identity/material 不一致。"""


class StrategyTransitionHeadConflictError(RuntimeError):
    """C17 current resolution-head CAS 或 exact pointer authority 發生衝突。"""


@runtime_checkable
class StrategyGoverningTransitionRepository(Protocol):
    """Pattern A descriptor + phase evidence + current resolution persistence port。"""

    def append_descriptor(
        self,
        authority: StrategyGoverningTransitionAuthority,
    ) -> None:
        ...

    def append_phase_evidence(
        self,
        evidence: StrategyGoverningTransitionPhaseEvidence,
    ) -> None:
        ...

    def append_resolution(
        self,
        receipt: StrategyGoverningTransitionResolutionReceipt,
    ) -> None:
        ...

    def advance_resolution_head(
        self,
        *,
        strategy_instance_id: str,
        resolution_id: str,
        expected_head_revision: int,
    ) -> int:
        ...

    def current_resolution(
        self,
        strategy_instance_id: str,
    ) -> StrategyGoverningTransitionResolution | None:
        ...


@runtime_checkable
class DecisionCohortAuthorityProvider(Protocol):
    """G / Decision Domain authority 的 C18 trusted provider seam。"""

    def resolve_required_membership(
        self,
        *,
        cohort_id: str,
        policy: DecisionPolicyAuthorityRef,
    ) -> RequiredCohortMembershipEvidence | None:
        ...


__all__ = [
    "DecisionCohortAuthorityProvider",
    "StrategyGoverningTransitionRepository",
    "StrategyTransitionHeadConflictError",
    "StrategyTransitionPersistenceIntegrityError",
]
