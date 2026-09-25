from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, field_validator

from persistence.contracts import normalize_aware_utc, normalize_stable_id


def _canonical_json_object(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("payload_json must be a JSON object")
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        normalized = json.loads(encoded)
    except (TypeError, ValueError) as exc:
        raise ValueError("payload_json must contain canonical JSON values") from exc
    return normalized


class TradingEvent(BaseModel):
    """Material trading fact 的 canonical immutable envelope；不承擔 projection 或執行。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: str
    event_type: str
    source: str
    entity_type: str
    entity_id: str
    occurred_at: datetime
    received_at: datetime
    sequence: int = Field(ge=0)
    event_version: int = Field(ge=1)
    idempotency_scope: str
    idempotency_key: str
    correlation_id: str | None = None
    causation_id: str | None = None
    payload_json: dict[str, Any]

    @field_validator(
        "event_id", "event_type", "source", "entity_type", "entity_id",
        "idempotency_scope", "idempotency_key", mode="before",
    )
    @classmethod
    def _normalize_required_ids(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_stable_id(value)
        return value

    @field_validator("correlation_id", "causation_id", mode="before")
    @classmethod
    def _normalize_optional_ids(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            return normalize_stable_id(value)
        return value

    @field_validator("occurred_at", "received_at")
    @classmethod
    def _normalize_timestamps(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)

    @field_validator("payload_json", mode="before")
    @classmethod
    def _normalize_payload(cls, value: object) -> dict[str, Any]:
        return _canonical_json_object(value)

    def canonical_json(self) -> str:
        """供 duplicate/conflict 判斷的 deterministic canonical representation。"""

        return self.model_dump_json(exclude_none=False)


class EventAppendStatus(str, Enum):
    APPENDED = "APPENDED"
    DUPLICATE = "DUPLICATE"


class EventAppendResult(BaseModel):
    """Append outcome；DUPLICATE 僅代表 persisted event 完全相同。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: EventAppendStatus
    event_id: str

    @field_validator("event_id", mode="before")
    @classmethod
    def _normalize_event_id(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_stable_id(value)
        return value


@runtime_checkable
class EventLedgerRepository(Protocol):
    """Append-only event ledger port；consumer 無法透過此介面 update/delete。"""

    def append(self, event: TradingEvent) -> EventAppendResult: ...
    def get(self, event_id: str) -> TradingEvent | None: ...
    def get_by_idempotency(self, scope: str, key: str) -> TradingEvent | None: ...
    def list_after(
        self,
        source: str,
        entity_type: str,
        entity_id: str,
        after_sequence: int,
        limit: int,
    ) -> tuple[TradingEvent, ...]: ...
