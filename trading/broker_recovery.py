from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from persistence.contracts import normalize_aware_utc, normalize_stable_id
from trading.account import BrokerAccount
from trading.execution import Fill, Order, OrderStatus


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


class BrokerRecoveryIntegrityError(RuntimeError):
    """Broker recovery evidence 不完整、衝突或超出 sealed terminal 時 fail closed。"""


class BrokerReconstructionIncompleteError(BrokerRecoveryIntegrityError):
    """Evidence 尚不足以接受 terminal/lifecycle authority；不得 fabricated progress。"""


class BrokerDealSetCompleteness(str, Enum):
    """Broker deal collection 是否明確聲稱涵蓋完整 required DealSet。"""

    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"


class BrokerLifecycleEvidence(BaseModel):
    """Broker-neutral lifecycle evidence；verified 不代表任何具體 broker production 能力。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    target_status: OrderStatus
    verified: bool
    original_order_failure: bool = False
    evidence: tuple[str, ...]

    @field_validator("evidence", mode="before")
    @classmethod
    def _evidence(cls, value: object) -> object:
        return tuple(normalize_stable_id(v) for v in value) if isinstance(value, (tuple, list)) else value

    @model_validator(mode="after")
    def _contract(self) -> "BrokerLifecycleEvidence":
        if not self.evidence:
            raise ValueError("broker lifecycle evidence is required")
        if self.original_order_failure and self.target_status is not OrderStatus.REJECTED:
            raise ValueError("original_order_failure only applies to REJECTED")
        return self


class BrokerDealIdentity(BaseModel):
    """Broker-neutral exact deal identity；禁止以 timestamp/price/quantity heuristic 代替。"""
    model_config = ConfigDict(extra="forbid", frozen=True)
    broker: str
    account_ref: str
    deal_id: str

    @field_validator("broker", mode="before")
    @classmethod
    def _broker(cls, value: object) -> object:
        return normalize_stable_id(value).upper() if isinstance(value, str) else value

    @field_validator("account_ref", "deal_id", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value


class BrokerDealEvidence(BaseModel):
    """已驗證 exact identity 的 broker deal evidence；aggregate 僅可作驗證資料。"""
    model_config = ConfigDict(extra="forbid", frozen=True)
    identity: BrokerDealIdentity
    order_id: str
    broker_client_order_ref: str
    quantity: int
    price: Decimal
    occurred_at: datetime
    identity_verified: bool

    @field_validator("order_id", "broker_client_order_ref", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("price", mode="before")
    @classmethod
    def _price(cls, value: object) -> Decimal:
        if not isinstance(value, Decimal) or not value.is_finite():
            raise ValueError("broker deal price must be a finite Decimal")
        return value

    @field_validator("occurred_at")
    @classmethod
    def _occurred_at(cls, value: datetime) -> datetime:
        return normalize_aware_utc(value)

    @model_validator(mode="after")
    def _material(self) -> "BrokerDealEvidence":
        if self.quantity <= 0:
            raise ValueError("broker deal quantity must be positive")
        if not self.identity_verified:
            raise BrokerRecoveryIntegrityError("broker deal identity is not verified")
        return self


class BrokerReconstructionPlan(BaseModel):
    """Pure reconstruction result；下游僅能以 complete canonical Fill set 投影 economics。"""
    model_config = ConfigDict(extra="forbid", frozen=True)
    status: OrderStatus
    accepted_fills: tuple[Fill, ...]
    filled_quantity: int
    average_fill_price: Decimal | None
    material_change: bool


def reconstruct_broker_order(
    *,
    order: Order,
    local_fills: tuple[Fill, ...],
    evidence: tuple[BrokerDealEvidence, ...],
    event_id: str,
    correlation_id: str,
    authority_broker: str,
    authority_account_ref: str,
    deal_set_completeness: BrokerDealSetCompleteness,
    lifecycle_evidence: BrokerLifecycleEvidence | None = None,
) -> BrokerReconstructionPlan:
    """從 exact deal evidence 建立 plan；不執行 broker I/O、不寫 authority。"""
    authority_broker = normalize_stable_id(authority_broker).upper()
    authority_account_ref = normalize_stable_id(authority_account_ref)
    for item in evidence:
        if (
            item.identity.broker != authority_broker
            or item.identity.account_ref != authority_account_ref
        ):
            raise BrokerRecoveryIntegrityError("broker deal account scope conflicts with authority mutation")
    evidence_ids = {item.identity.deal_id for item in evidence}
    local_identified = tuple(fill for fill in local_fills if fill.broker_deal_id is not None)
    local_ids = {fill.broker_deal_id for fill in local_identified}
    if deal_set_completeness is BrokerDealSetCompleteness.COMPLETE:
        if len(local_identified) != len(local_fills) or not local_ids.issubset(evidence_ids):
            raise BrokerRecoveryIntegrityError("complete broker DealSet is a proper subset of LocalFillSet")
    if order.status in {OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED}:
        by_deal = {fill.broker_deal_id: fill for fill in local_fills if fill.broker_deal_id}
        for item in evidence:
            existing = by_deal.get(item.identity.deal_id)
            if (
                existing is None
                or existing.quantity != item.quantity
                or existing.price != item.price
                or existing.occurred_at != item.occurred_at
            ):
                raise BrokerRecoveryIntegrityError("terminal order economics are sealed")
        return BrokerReconstructionPlan(
            status=order.status,
            accepted_fills=(),
            filled_quantity=order.filled_quantity,
            average_fill_price=order.average_fill_price,
            material_change=False,
        )
    by_deal = {fill.broker_deal_id: fill for fill in local_fills if fill.broker_deal_id}
    if len(by_deal) != len([fill for fill in local_fills if fill.broker_deal_id]):
        raise BrokerRecoveryIntegrityError("canonical Fill set has duplicate deal identity")
    accepted: list[Fill] = []
    seen: dict[str, BrokerDealEvidence] = {}
    for item in evidence:
        if item.order_id != order.order_id or item.broker_client_order_ref != order.broker_client_order_ref:
            raise BrokerRecoveryIntegrityError("broker deal does not match canonical order identity")
        deal_id = item.identity.deal_id
        if deal_id in seen and seen[deal_id] != item:
            raise BrokerRecoveryIntegrityError("broker deal identity has conflicting content")
        seen[deal_id] = item
        existing = by_deal.get(deal_id)
        candidate = Fill(
            fill_id=f"BROKER-DEAL:{item.identity.broker}:{item.identity.account_ref}:{deal_id}",
            order_id=order.order_id,
            event_id=event_id,
            correlation_id=correlation_id,
            causation_id=event_id,
            quantity=item.quantity,
            price=item.price,
            occurred_at=item.occurred_at,
            broker_deal_id=deal_id,
        )
        if existing is not None:
            if (
                existing.order_id != candidate.order_id
                or existing.quantity != candidate.quantity
                or existing.price != candidate.price
                or existing.occurred_at != candidate.occurred_at
            ):
                raise BrokerRecoveryIntegrityError("broker deal conflicts with canonical Fill")
            continue
        if deal_id not in {fill.broker_deal_id for fill in accepted}:
            accepted.append(candidate)
    complete = local_fills + tuple(accepted)
    quantity = sum(fill.quantity for fill in complete)
    if quantity > order.quantity:
        raise BrokerRecoveryIntegrityError("canonical Fill quantity exceeds order quantity")
    average = None if quantity == 0 else sum(fill.price * fill.quantity for fill in complete) / Decimal(quantity)
    if lifecycle_evidence is not None and not lifecycle_evidence.verified:
        raise BrokerReconstructionIncompleteError("broker lifecycle evidence is not verified")
    if quantity == order.quantity:
        if deal_set_completeness is not BrokerDealSetCompleteness.COMPLETE:
            raise BrokerReconstructionIncompleteError("FILLED requires a complete identifiable broker DealSet")
        status = OrderStatus.FILLED
    elif quantity > 0:
        status = OrderStatus.PARTIALLY_FILLED
    else:
        status = order.status

    if lifecycle_evidence is not None:
        target = lifecycle_evidence.target_status
        if target is OrderStatus.REJECTED:
            if not lifecycle_evidence.original_order_failure or quantity != 0:
                raise BrokerRecoveryIntegrityError("REJECTED requires verified zero-economic original-order failure")
            if deal_set_completeness is not BrokerDealSetCompleteness.COMPLETE:
                raise BrokerReconstructionIncompleteError("REJECTED requires complete zero-economic evidence")
            status = target
        elif target is OrderStatus.CANCELLED:
            if quantity >= order.quantity:
                raise BrokerRecoveryIntegrityError("CANCELLED requires filled quantity below order quantity")
            if deal_set_completeness is not BrokerDealSetCompleteness.COMPLETE:
                raise BrokerReconstructionIncompleteError("CANCELLED requires complete economic evidence")
            status = target
        elif target is OrderStatus.SUBMITTED:
            if quantity != 0:
                raise BrokerRecoveryIntegrityError("SUBMITTED lifecycle evidence conflicts with Fill economics")
            status = target
        elif target not in {status, OrderStatus.PENDING}:
            raise BrokerRecoveryIntegrityError("broker lifecycle evidence conflicts with Fill-derived status")

    material_change = status is not order.status or bool(accepted)
    if status is OrderStatus.PARTIALLY_FILLED and not (0 < quantity < order.quantity):
        raise BrokerRecoveryIntegrityError("PARTIALLY_FILLED requires partial canonical Fill economics")
    if status is OrderStatus.PARTIALLY_FILLED and order.status is OrderStatus.PARTIALLY_FILLED and not accepted:
        material_change = False
    return BrokerReconstructionPlan(
        status=status,
        accepted_fills=tuple(accepted),
        filled_quantity=quantity,
        average_fill_price=average,
        material_change=material_change,
    )


__all__ = ["BrokerDealEvidence", "BrokerDealIdentity", "BrokerDealSetCompleteness", "BrokerDiscoveryError", "BrokerDiscoveryIntegrity", "BrokerDiscoveryRequest", "BrokerDiscoveryResult", "BrokerDiscoveryScopeError", "BrokerLifecycleEvidence", "BrokerOrderDiscoveryProvider", "BrokerOrderObservation", "BrokerReconstructionIncompleteError", "BrokerReconstructionPlan", "BrokerRecoveryIntegrityError", "DiscoveryCompleteness", "ExactMatchCardinality", "classify_broker_discovery", "reconstruct_broker_order"]
