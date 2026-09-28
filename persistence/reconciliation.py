from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import Enum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from persistence.contracts import normalize_aware_utc, normalize_stable_id
from trading.reconciliation import (
    ReconciliationCase,
    ReconciliationCaseState,
    ReconciliationPolicy,
    ReconciliationResult,
    ReconciliationStatus,
)
from trading.account import BrokerAccount


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

    @model_validator(mode="after")
    def _identity_matches_case(self) -> "ReconciliationCaseVersion":
        if self.case_id != self.reconciliation_case.case_id:
            raise ValueError("case_id must match reconciliation_case.case_id")
        return self


@runtime_checkable
class ReconciliationCaseRepository(Protocol):
    def append(self, version: ReconciliationCaseVersion) -> None: ...
    def latest(self, case_id: str) -> ReconciliationCaseVersion | None: ...
    def unresolved(self, account: BrokerAccount) -> tuple[ReconciliationCaseVersion, ...]: ...


def blocking_case_state(versions: tuple[ReconciliationCaseVersion, ...]) -> ReconciliationCaseState | None:
    states = {item.reconciliation_case.state for item in versions}
    if ReconciliationCaseState.HALT in states: return ReconciliationCaseState.HALT
    if ReconciliationCaseState.REVIEW_REQUIRED in states: return ReconciliationCaseState.REVIEW_REQUIRED
    return None


def reconciliation_blocker_semantic_fingerprint(
    versions: tuple[ReconciliationCaseVersion, ...],
) -> str:
    """封存 C13 readiness semantics；排除 version、時間與 actor 等 audit wrapper。"""

    ordered=tuple(sorted(versions,key=lambda item:item.case_id))
    if len({item.case_id for item in ordered}) != len(ordered):
        raise ReconciliationCaseError("duplicate unresolved reconciliation case ID")
    material=[
        {
            "case_id":item.case_id,
            "account":item.reconciliation_case.account.model_dump(mode="json"),
            "result":item.reconciliation_case.result.model_dump(mode="json"),
            "policy":item.reconciliation_case.policy.value,
            "state":item.reconciliation_case.state.value,
        }
        for item in ordered
    ]
    encoded=json.dumps(material,sort_keys=True,separators=(",",":"),ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class ReconciliationRunTechnicalOutcome(str, Enum):
    """Formal evaluation 的技術執行結果；與 domain mismatch 分離。"""

    COMPLETED = "COMPLETED"
    EXTERNAL_STATE_UNKNOWN = "EXTERNAL_STATE_UNKNOWN"
    FAILED = "FAILED"


class ReconciliationInputQualification(str, Enum):
    """輸入世界是否具備 formal domain 判斷資格。"""

    QUALIFIED = "QUALIFIED"
    UNQUALIFIED = "UNQUALIFIED"


class ReconciliationRunBoundary(BaseModel):
    """先於 formal evaluation durable 建立的 BrokerAccount-scoped evaluated-world boundary。"""

    model_config=ConfigDict(extra="forbid",frozen=True)

    run_id: str
    account: BrokerAccount
    policy: ReconciliationPolicy
    recovery_cut_fingerprint: str
    account_revision: int = Field(ge=0)
    expected_snapshot_id: str
    authority_commit_id: str
    recovery_generation: int | None = Field(default=None,ge=1)
    recovery_ingress_version: int | None = Field(default=None,ge=0)
    discovery_run_id: str | None = None
    observation_id: str | None = None
    established_at: datetime

    @field_validator("run_id","recovery_cut_fingerprint","expected_snapshot_id","authority_commit_id","discovery_run_id","observation_id",mode="before")
    @classmethod
    def _ids(cls,value: object) -> object:
        return None if value is None else normalize_stable_id(value)  # type: ignore[arg-type]

    @field_validator("established_at")
    @classmethod
    def _time(cls,value: datetime) -> datetime: return normalize_aware_utc(value)

    @model_validator(mode="after")
    def _witness(self) -> "ReconciliationRunBoundary":
        if (self.recovery_generation is None) != (self.recovery_ingress_version is None):
            raise ValueError("recovery currentness witness must be complete")
        return self


class ReconciliationRunOutcome(BaseModel):
    """單一 authoritative terminal audit；required results 與 provenance 同一筆原子 finalize。"""

    model_config=ConfigDict(extra="forbid",frozen=True)

    run_id: str
    technical_outcome: ReconciliationRunTechnicalOutcome
    input_qualification: ReconciliationInputQualification
    results: tuple[ReconciliationResult,...]
    finalized_at: datetime
    evidence: tuple[str,...]

    @field_validator("run_id",mode="before")
    @classmethod
    def _run_id(cls,value: object) -> object: return normalize_stable_id(value) if isinstance(value,str) else value

    @field_validator("finalized_at")
    @classmethod
    def _time(cls,value: datetime) -> datetime: return normalize_aware_utc(value)

    @field_validator("evidence",mode="before")
    @classmethod
    def _evidence(cls,value: object) -> object:
        return tuple(normalize_stable_id(item) for item in value) if isinstance(value,(tuple,list)) else value

    @model_validator(mode="after")
    def _terminal_contract(self) -> "ReconciliationRunOutcome":
        if not self.evidence:
            raise ValueError("terminal reconciliation run requires evidence")
        if self.input_qualification is ReconciliationInputQualification.UNQUALIFIED and any(item.status is ReconciliationStatus.MATCH for item in self.results):
            raise ValueError("unqualified inputs cannot produce MATCH")
        if self.technical_outcome is ReconciliationRunTechnicalOutcome.EXTERNAL_STATE_UNKNOWN and not any(item.status is ReconciliationStatus.UNKNOWN_EXTERNAL_STATE for item in self.results):
            raise ValueError("external-state-unknown outcome requires UNKNOWN result")
        if self.technical_outcome is not ReconciliationRunTechnicalOutcome.COMPLETED and self.input_qualification is ReconciliationInputQualification.QUALIFIED:
            raise ValueError("non-completed technical outcome cannot claim qualified input")
        return self


@runtime_checkable
class ReconciliationRunRepository(Protocol):
    """Append-only formal run audit port；不推進 AccountStateHead。"""

    def establish(self,boundary: ReconciliationRunBoundary) -> None: ...
    def finalize(self,outcome: ReconciliationRunOutcome) -> None: ...
    def get_boundary(self,run_id: str) -> ReconciliationRunBoundary | None: ...
    def get_outcome(self,run_id: str) -> ReconciliationRunOutcome | None: ...
