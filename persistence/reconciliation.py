from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, field_validator

from persistence.contracts import normalize_aware_utc, normalize_stable_id
from trading.reconciliation import ReconciliationCase, ReconciliationCaseState


class ReconciliationCaseVersion(BaseModel):
    """Append-only case history version；resolution 建立新版本而非 overwrite。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    case_id: str
    version: int = Field(ge=1)
    recorded_at: datetime
    reconciliation_case: ReconciliationCase
    actor_ref: str | None = None
    evidence: tuple[str, ...] = ()

    @field_validator("case_id", "actor_ref", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return None if value is None else normalize_stable_id(value)  # type: ignore[arg-type]

    @field_validator("recorded_at")
    @classmethod
    def _utc(cls, value: datetime) -> datetime: return normalize_aware_utc(value)


@runtime_checkable
class ReconciliationCaseRepository(Protocol):
    def append(self, version: ReconciliationCaseVersion) -> None: ...
    def latest(self, case_id: str) -> ReconciliationCaseVersion | None: ...
    def unresolved(self) -> tuple[ReconciliationCaseVersion, ...]: ...


def blocking_case_state(versions: tuple[ReconciliationCaseVersion, ...]) -> ReconciliationCaseState | None:
    states = {item.reconciliation_case.state for item in versions}
    if ReconciliationCaseState.HALT in states: return ReconciliationCaseState.HALT
    if ReconciliationCaseState.REVIEW_REQUIRED in states: return ReconciliationCaseState.REVIEW_REQUIRED
    return None
