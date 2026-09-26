
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Protocol, runtime_checkable

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from domain.market_observation import (
    MarketObservationRevisionId,
)
from persistence.contracts import (
    normalize_aware_utc,
    normalize_stable_id,
)
from strategy.instance import canonical_config_json


class LegacyMarketObservationReferenceError(
    ValueError
):
    """Legacy/free-form observation reference ???? canonical recovery authority?"""


class StrategyStateReferenceConflictError(
    ValueError
):
    """Legacy ? canonical MarketObservation revision reference ????"""


def normalize_market_observation_revision_id(
    value: object,
) -> str:
    """?? recovery authority ??? C23 mor1 revision-specific identity?"""

    if isinstance(
        value,
        MarketObservationRevisionId,
    ):
        return value.value

    if not isinstance(
        value,
        str,
    ):
        raise (
            LegacyMarketObservationReferenceError(
                "market observation revision "
                "reference must be string or "
                "MarketObservationRevisionId"
            )
        )

    normalized = normalize_stable_id(
        value
    )

    try:
        return MarketObservationRevisionId(
            normalized
        ).value
    except ValueError as exc:
        raise (
            LegacyMarketObservationReferenceError(
                "market observation recovery "
                "authority must use mor1 "
                "revision identity"
            )
        ) from exc


class StrategyStateSnapshot(
    BaseModel
):
    """Completed durable MarketObservation revision boundary strategy state?"""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    snapshot_id: str
    strategy_instance_id: str
    strategy_id: str
    strategy_version: str
    config_version: str
    config_fingerprint: str
    instrument_id: int = Field(
        gt=0
    )
    timeframe: str
    state_schema_version: int = Field(
        ge=1
    )
    last_market_observation_revision_id: str
    captured_at: datetime
    state_json: dict[str, object]

    @model_validator(
        mode="before"
    )
    @classmethod
    def _canonical_reference(
        cls,
        value: object,
    ) -> object:
        if not isinstance(
            value,
            Mapping,
        ):
            return value

        data = dict(value)

        canonical_raw = data.get(
            "last_market_observation_revision_id"
        )

        legacy_present = (
            "last_market_observation_id"
            in data
        )

        legacy_raw = data.pop(
            "last_market_observation_id",
            None,
        )

        canonical = (
            None
            if canonical_raw is None
            else (
                normalize_market_observation_revision_id(
                    canonical_raw
                )
            )
        )

        legacy = (
            None
            if not legacy_present
            else (
                normalize_market_observation_revision_id(
                    legacy_raw
                )
            )
        )

        if canonical is None:
            canonical = legacy

        if canonical is None:
            raise (
                LegacyMarketObservationReferenceError(
                    "last_market_observation_"
                    "revision_id is required"
                )
            )

        if (
            legacy is not None
            and legacy != canonical
        ):
            raise (
                StrategyStateReferenceConflictError(
                    "legacy/canonical market "
                    "observation references disagree"
                )
            )

        data[
            "last_market_observation_revision_id"
        ] = canonical

        return data

    @field_validator(
        "snapshot_id",
        "strategy_instance_id",
        "strategy_id",
        "strategy_version",
        "config_version",
        "config_fingerprint",
        "timeframe",
        mode="before",
    )
    @classmethod
    def _ids(
        cls,
        value: object,
    ) -> object:
        if isinstance(
            value,
            str,
        ):
            return normalize_stable_id(
                value
            )

        return value

    @field_validator(
        "last_market_observation_revision_id",
        mode="before",
    )
    @classmethod
    def _revision_id(
        cls,
        value: object,
    ) -> str:
        return (
            normalize_market_observation_revision_id(
                value
            )
        )

    @field_validator(
        "captured_at"
    )
    @classmethod
    def _utc(
        cls,
        value: datetime,
    ) -> datetime:
        return normalize_aware_utc(
            value
        )

    @field_validator(
        "state_json",
        mode="before",
    )
    @classmethod
    def _state(
        cls,
        value: object,
    ) -> dict[str, object]:
        return canonical_config_json(
            value
        )

    @property
    def last_market_observation_id(
        self,
    ) -> str:
        """Compatibility read surface???? canonical mor1?????????"""

        return (
            self.last_market_observation_revision_id
        )


@runtime_checkable
class StrategyInstanceRepository(
    Protocol
):
    def get(
        self,
        strategy_instance_id: str,
    ):
        ...


@runtime_checkable
class StrategyStateRepository(
    Protocol
):
    def append(
        self,
        snapshot: StrategyStateSnapshot,
    ) -> None:
        ...

    def latest(
        self,
        strategy_instance_id: str,
    ) -> (
        StrategyStateSnapshot
        | None
    ):
        ...


__all__ = [
    "LegacyMarketObservationReferenceError",
    "StrategyInstanceRepository",
    "StrategyStateReferenceConflictError",
    "StrategyStateRepository",
    "StrategyStateSnapshot",
    "normalize_market_observation_revision_id",
]
