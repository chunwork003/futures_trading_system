from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from persistence.contracts import normalize_aware_utc, normalize_stable_id
from trading.account import BrokerAccount


class DiscoveryCompleteness(str, Enum):
    """Discovery 是否完整涵蓋 request 明定的 scope、horizon 與 refresh world。"""
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"


class ExactMatchCardinality(str, Enum):
    """以 exact broker client correlation identity 計算的 match cardinality。"""
    ZERO = "ZERO"
    ONE = "ONE"
    MULTIPLE = "MULTIPLE"


class BrokerDiscoveryIntegrity(str, Enum):
    """Discovery 結果的 broker-neutral integrity classification。"""
    CONSISTENT = "CONSISTENT"
    AMBIGUOUS_EXACT_MATCH = "AMBIGUOUS_EXACT_MATCH"


class BrokerDiscoveryError(RuntimeError):
    """唯讀 broker discovery query failure，保留精確帳戶範圍。"""
    def __init__(self, account: BrokerAccount, message: str) -> None:
        self.broker, self.account_ref = account.broker, account.account_ref
        super().__init__(normalize_stable_id(message))


class BrokerDiscoveryScopeError(ValueError):
    """Provider evidence 不屬於 request BrokerAccount 時 fail closed。"""


class BrokerOrderObservation(BaseModel):
    """Broker-neutral order observation；不保存 native object，client ref 不是 idempotency authority。"""
    model_config = ConfigDict(extra="forbid", frozen=True)
    broker: str
    account_ref: str
    broker_order_id: str
    broker_client_order_ref: str
    observed_at: datetime
    payload_fingerprint: str

    @field_validator("account_ref", "broker_order_id", "broker_client_order_ref", "payload_fingerprint", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("broker", mode="before")
    @classmethod
    def _broker(cls, value: object) -> object:
        return normalize_stable_id(value).upper() if isinstance(value, str) else value

    @field_validator("observed_at")
    @classmethod
    def _time(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)


class BrokerDiscoveryRequest(BaseModel):
    """一次 restart-safe discovery world 的 explicit read-only request；禁止 cache/heuristic 代替 authority。"""
    model_config = ConfigDict(extra="forbid", frozen=True)
    discovery_run_id: str
    account: BrokerAccount
    broker_client_order_ref: str
    required_scope: str
    horizon_start: datetime
    horizon_end: datetime
    refresh_required: bool = True

    @field_validator("discovery_run_id", "broker_client_order_ref", "required_scope", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("horizon_start", "horizon_end")
    @classmethod
    def _time(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)

    @model_validator(mode="after")
    def _horizon(self) -> "BrokerDiscoveryRequest":
        if self.horizon_start > self.horizon_end:
            raise ValueError("discovery horizon_start must not exceed horizon_end")
        return self


class BrokerDiscoveryResult(BaseModel):
    """Immutable discovery evidence；completeness 與 cardinality 分離且不授權 blind retry。"""
    model_config = ConfigDict(extra="forbid", frozen=True)
    discovery_run_id: str
    account: BrokerAccount
    required_scope: str
    horizon_start: datetime
    horizon_end: datetime
    refreshed_at: datetime | None
    completeness: DiscoveryCompleteness
    exact_matches: tuple[BrokerOrderObservation, ...]
    cardinality: ExactMatchCardinality
    integrity: BrokerDiscoveryIntegrity
    evidence: tuple[str, ...]

    @field_validator("discovery_run_id", "required_scope", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("horizon_start", "horizon_end", "refreshed_at")
    @classmethod
    def _time(cls, value: datetime | None) -> datetime | None:
        return None if value is None else normalize_aware_utc(value)

    @field_validator("evidence", mode="before")
    @classmethod
    def _evidence(cls, value: object) -> object:
        return tuple(normalize_stable_id(v) for v in value) if isinstance(value, (tuple, list)) else value

    @model_validator(mode="after")
    def _world(self) -> "BrokerDiscoveryResult":
        cardinality = ExactMatchCardinality.ZERO if not self.exact_matches else ExactMatchCardinality.ONE if len(self.exact_matches) == 1 else ExactMatchCardinality.MULTIPLE
        if self.cardinality is not cardinality:
            raise ValueError("exact-match cardinality does not match evidence")
        integrity = BrokerDiscoveryIntegrity.AMBIGUOUS_EXACT_MATCH if cardinality is ExactMatchCardinality.MULTIPLE else BrokerDiscoveryIntegrity.CONSISTENT
        if self.integrity is not integrity:
            raise ValueError("discovery integrity does not match cardinality")
        if any(o.broker != self.account.broker or o.account_ref != self.account.account_ref for o in self.exact_matches):
            raise BrokerDiscoveryScopeError("broker discovery evidence belongs to a different account")
        if self.completeness is DiscoveryCompleteness.COMPLETE and self.refreshed_at is None:
            raise ValueError("complete discovery requires refresh evidence")
        if self.completeness is DiscoveryCompleteness.COMPLETE and not self.evidence:
            raise ValueError("complete discovery requires scope/horizon evidence")
        return self

    def proves_no_exact_match_in_verified_scope(self, *, unresolved_attempt_exists: bool) -> bool:
        """只證明 verified world 內 absence；unresolved attempt 永遠否決 retry inference。"""
        return not unresolved_attempt_exists and self.completeness is DiscoveryCompleteness.COMPLETE and self.cardinality is ExactMatchCardinality.ZERO


@runtime_checkable
class BrokerOrderDiscoveryProvider(Protocol):
    """唯讀 broker-neutral discovery port；不包含 submit/cancel 或 native cache。"""
    def discover(self, request: BrokerDiscoveryRequest) -> BrokerDiscoveryResult: ...


def classify_broker_discovery(*, request: BrokerDiscoveryRequest, observations: tuple[BrokerOrderObservation, ...], completeness: DiscoveryCompleteness, refreshed_at: datetime | None, evidence: tuple[str, ...]) -> BrokerDiscoveryResult:
    """只以 exact client ref 分類；不使用屬性、時間窗或數值 heuristic。"""
    if any(o.broker != request.account.broker or o.account_ref != request.account.account_ref for o in observations):
        raise BrokerDiscoveryScopeError("broker discovery evidence belongs to a different account")
    matches = tuple(o for o in observations if o.broker_client_order_ref == request.broker_client_order_ref)
    cardinality = ExactMatchCardinality.ZERO if not matches else ExactMatchCardinality.ONE if len(matches) == 1 else ExactMatchCardinality.MULTIPLE
    integrity = BrokerDiscoveryIntegrity.AMBIGUOUS_EXACT_MATCH if cardinality is ExactMatchCardinality.MULTIPLE else BrokerDiscoveryIntegrity.CONSISTENT
    return BrokerDiscoveryResult(discovery_run_id=request.discovery_run_id, account=request.account, required_scope=request.required_scope, horizon_start=request.horizon_start, horizon_end=request.horizon_end, refreshed_at=refreshed_at, completeness=completeness, exact_matches=matches, cardinality=cardinality, integrity=integrity, evidence=evidence)


__all__ = ["BrokerDiscoveryError", "BrokerDiscoveryIntegrity", "BrokerDiscoveryRequest", "BrokerDiscoveryResult", "BrokerDiscoveryScopeError", "BrokerOrderDiscoveryProvider", "BrokerOrderObservation", "DiscoveryCompleteness", "ExactMatchCardinality", "classify_broker_discovery"]
