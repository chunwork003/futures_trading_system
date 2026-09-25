from __future__ import annotations

import json
from datetime import datetime
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, field_validator

from persistence.contracts import normalize_aware_utc, normalize_stable_id
from strategy.instance import canonical_config_json


class StrategyStateSnapshot(BaseModel):
    """Completed market observation boundary 的 versioned logical strategy state。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    snapshot_id: str
    strategy_instance_id: str
    strategy_id: str
    strategy_version: str
    config_version: str
    config_fingerprint: str
    instrument_id: int = Field(gt=0)
    timeframe: str
    state_schema_version: int = Field(ge=1)
    last_market_observation_id: str
    captured_at: datetime
    state_json: dict[str, object]

    @field_validator("snapshot_id", "strategy_instance_id", "strategy_id", "strategy_version", "config_version", "config_fingerprint", "timeframe", "last_market_observation_id", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("captured_at")
    @classmethod
    def _utc(cls, value: datetime) -> datetime: return normalize_aware_utc(value)

    @field_validator("state_json", mode="before")
    @classmethod
    def _state(cls, value: object) -> dict[str, object]: return canonical_config_json(value)


@runtime_checkable
class StrategyInstanceRepository(Protocol):
    def get(self, strategy_instance_id: str): ...


@runtime_checkable
class StrategyStateRepository(Protocol):
    def append(self, snapshot: StrategyStateSnapshot) -> None: ...
    def latest(self, strategy_instance_id: str) -> StrategyStateSnapshot | None: ...
