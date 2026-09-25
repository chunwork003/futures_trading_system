from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from persistence.contracts import normalize_stable_id


def canonical_config_json(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("config_json must be a JSON object")
    try:
        return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False))
    except (TypeError, ValueError) as exc:
        raise ValueError("config_json must contain JSON values") from exc


def config_fingerprint(value: dict[str, object]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class StrategyInstance(BaseModel):
    """Immutable strategy/config/scope identity；material config change 必須建立新 identity/version。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    strategy_instance_id: str
    strategy_id: str
    strategy_version: str
    config_version: str
    config_fingerprint: str
    instrument_id: int = Field(gt=0)
    timeframe: str
    config_json: dict[str, object]

    @field_validator("strategy_instance_id", "strategy_id", "strategy_version", "config_version", "timeframe", mode="before")
    @classmethod
    def _text(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("config_json", mode="before")
    @classmethod
    def _config(cls, value: object) -> dict[str, object]: return canonical_config_json(value)

    @model_validator(mode="after")
    def _fingerprint(self) -> "StrategyInstance":
        if self.config_fingerprint != config_fingerprint(self.config_json):
            raise ValueError("config_fingerprint does not match canonical config_json")
        return self
