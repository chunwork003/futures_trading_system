
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from domain.market_observation import (
    MarketObservationRevisionId,
)
from domain.market_observation_acceptance import (
    MarketObservationAcceptancePolicy,
    MarketObservationCandidateEvidence,
    MarketObservationRevision,
)
from persistence.contracts import (
    UnitOfWork,
)
from persistence.market_observation import (
    MarketObservationAcceptanceRepository,
    MarketObservationAcceptanceResult,
)
from trading.execution import (
    ExecutionTriggerRef,
)


class MarketObservationStrategyDeliveryError(
    RuntimeError
):
    """Durable-before-strategy delivery contract failure?"""


class MarketObservationStrategyDeliveryBlockedError(
    MarketObservationStrategyDeliveryError
):
    """Quarantine/integrity evidence ?? material strategy delivery?"""


class MarketObservationRevisionResolutionError(
    MarketObservationStrategyDeliveryError
):
    """Commit ? exact accepted revision ?????"""


@dataclass(
    frozen=True,
    slots=True,
)
class DurableMarketObservationDeliveryResult:
    acceptance_result: (
        MarketObservationAcceptanceResult
    )
    revision: MarketObservationRevision
    execution_trigger_ref: ExecutionTriggerRef
    consumer_result: object


class DurableMarketObservationStrategyDelivery:
    """C24 evidence durable ???? recovery-capable strategy consume?"""

    def __init__(
        self,
        *,
        uow_factory: Callable[
            [],
            UnitOfWork,
        ],
        repository_factory: Callable[
            [UnitOfWork],
            MarketObservationAcceptanceRepository,
        ],
        revision_loader: Callable[
            [MarketObservationRevisionId],
            (
                MarketObservationRevision
                | None
            ),
        ],
    ) -> None:
        self._uow_factory = uow_factory
        self._repository_factory = (
            repository_factory
        )
        self._revision_loader = (
            revision_loader
        )

    def deliver(
        self,
        *,
        policy: (
            MarketObservationAcceptancePolicy
        ),
        candidate: (
            MarketObservationCandidateEvidence
        ),
        decision_id: str,
        decided_at: datetime,
        consumer: Callable[
            [MarketObservationRevision],
            object,
        ],
    ) -> DurableMarketObservationDeliveryResult:
        acceptance_result: (
            MarketObservationAcceptanceResult
            | None
        ) = None

        # C24 mutation transaction.
        with self._uow_factory() as uow:
            repository = (
                self._repository_factory(
                    uow
                )
            )

            acceptance_result = (
                repository.process_candidate(
                    policy=policy,
                    candidate=candidate,
                    decision_id=decision_id,
                    decided_at=decided_at,
                )
            )

            # Candidate/decision/quarantine evidence
            # ??? durable?
            uow.commit()

        # ??? mutation UoW / row-lock lifetime?
        if acceptance_result is None:
            raise (
                MarketObservationRevisionResolutionError(
                    "committed acceptance result "
                    "is missing"
                )
            )

        if (
            acceptance_result.quarantined
            or (
                acceptance_result.integrity_error
                is not None
            )
        ):
            raise (
                MarketObservationStrategyDeliveryBlockedError(
                    "market observation evidence "
                    "is quarantined or "
                    "integrity-conflicted"
                )
            )

        revision_id = (
            acceptance_result.current_revision_id
        )

        if revision_id is None:
            raise (
                MarketObservationRevisionResolutionError(
                    "committed acceptance result "
                    "has no exact accepted revision ID"
                )
            )

        revision = self._revision_loader(
            revision_id
        )

        if revision is None:
            raise (
                MarketObservationRevisionResolutionError(
                    "committed accepted revision "
                    "cannot be resolved by exact mor1 ID"
                )
            )

        if (
            revision.observation_revision_id
            != revision_id
        ):
            raise (
                MarketObservationRevisionResolutionError(
                    "resolved revision identity "
                    "does not match committed reference"
                )
            )

        trigger_ref = ExecutionTriggerRef(
            market_observation_revision_id=(
                revision
                .observation_revision_id
                .value
            )
        )

        # Strategy callback ???? durable commit
        # ? mutation UoW exit ???
        consumer_result = consumer(
            revision
        )

        return (
            DurableMarketObservationDeliveryResult(
                acceptance_result=(
                    acceptance_result
                ),
                revision=revision,
                execution_trigger_ref=trigger_ref,
                consumer_result=consumer_result,
            )
        )


__all__ = [
    "DurableMarketObservationDeliveryResult",
    "DurableMarketObservationStrategyDelivery",
    "MarketObservationRevisionResolutionError",
    "MarketObservationStrategyDeliveryBlockedError",
    "MarketObservationStrategyDeliveryError",
]
