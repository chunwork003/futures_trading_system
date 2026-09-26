from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from persistence.contracts import normalize_aware_utc, normalize_stable_id, require_exact_decimal

from trading.account import AccountPosition, PositionDirection


class PositionEffect(str, Enum):
    """OrderIntent 對既有實體部位的明確影響。"""

    OPEN = "OPEN"
    REDUCE = "REDUCE"
    CLOSE = "CLOSE"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


TERMINAL_ORDER_STATUSES = frozenset(
    {OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED}
)

LEGAL_ORDER_TRANSITIONS = {
    OrderStatus.PENDING: frozenset(
        {OrderStatus.SUBMITTED, OrderStatus.CANCELLED, OrderStatus.REJECTED}
    ),
    OrderStatus.SUBMITTED: frozenset(
        {OrderStatus.PARTIALLY_FILLED, OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED}
    ),
    OrderStatus.PARTIALLY_FILLED: frozenset(
        {OrderStatus.PARTIALLY_FILLED, OrderStatus.FILLED, OrderStatus.CANCELLED}
    ),
}


class OrderStateTransitionError(ValueError):
    """Order event 不符合 frozen lifecycle、sequence 或 terminal invariant。"""


class _ExecutionModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    @field_validator("*", mode="before")
    @classmethod
    def _normalize_known_ids(cls, value: object, info):
        if info.field_name.endswith("_id") and value is not None and isinstance(value, str):
            return normalize_stable_id(value)
        return value


class Order(_ExecutionModel):
    """Canonical derived order projection；historical authority remains OrderEvent/Fill。"""

    order_id: str
    intent_id: str
    correlation_id: str
    causation_id: str | None = None
    broker_order_id: str | None = None
    instrument_id: int = Field(gt=0)
    contract_id: int | None = Field(default=None, gt=0)
    direction: PositionDirection
    position_effect: PositionEffect
    order_type: OrderType
    quantity: int = Field(gt=0)
    limit_price: Decimal | None = None
    stop_price: Decimal | None = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = Field(default=0, ge=0)
    average_fill_price: Decimal | None = None
    version: int = Field(default=0, ge=0)
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at")
    @classmethod
    def _utc(cls, value: datetime) -> datetime: return normalize_aware_utc(value)

    @field_validator("limit_price", "stop_price", "average_fill_price", mode="before")
    @classmethod
    def _decimal(cls, value: object) -> object:
        return None if value is None else require_exact_decimal(value)  # type: ignore[arg-type]

    @model_validator(mode="after")
    def _quantity_invariant(self) -> "Order":
        if self.filled_quantity > self.quantity:
            raise ValueError("filled_quantity cannot exceed quantity")
        return self


class Fill(_ExecutionModel):
    """Immutable execution evidence；broker identifiers remain opaque references。"""

    fill_id: str
    order_id: str
    event_id: str
    correlation_id: str
    causation_id: str
    quantity: int = Field(gt=0)
    price: Decimal
    occurred_at: datetime
    broker_trade_id: str | None = None
    broker_deal_id: str | None = None

    @field_validator("price", mode="before")
    @classmethod
    def _exact_price(cls, value: object) -> Decimal: return require_exact_decimal(value)  # type: ignore[arg-type]

    @field_validator("occurred_at")
    @classmethod
    def _utc(cls, value: datetime) -> datetime: return normalize_aware_utc(value)


class OrderEvent(_ExecutionModel):
    """Order lifecycle 的 immutable canonical evidence，sequence 由 OMS 嚴格驗證。"""

    event_id: str
    order_id: str
    correlation_id: str
    causation_id: str
    idempotency_key: str
    sequence: int = Field(ge=0)
    previous_status: OrderStatus | None
    status: OrderStatus
    occurred_at: datetime
    received_at: datetime
    broker_order_id: str | None = None
    payload_json: dict[str, object] = Field(default_factory=dict)

    @field_validator("occurred_at", "received_at")
    @classmethod
    def _utc(cls, value: datetime) -> datetime: return normalize_aware_utc(value)

    @model_validator(mode="after")
    def _creation_invariant(self) -> "OrderEvent":
        if self.sequence == 0:
            if self.previous_status is not None or self.status is not OrderStatus.PENDING:
                raise ValueError("sequence 0 must create None -> PENDING")
        elif self.previous_status is None:
            raise ValueError("subsequent event requires previous_status")
        return self


def validate_order_event_transition(previous: OrderEvent | None, current: OrderEvent) -> None:
    """驗證 contiguous sequence 與 frozen transition table；duplicate 由 ledger 先處理。"""

    if previous is None:
        if current.sequence != 0:
            raise OrderStateTransitionError("creation event sequence must be 0")
        return
    if current.order_id != previous.order_id or current.correlation_id != previous.correlation_id:
        raise OrderStateTransitionError("order event identity mismatch")
    if current.sequence != previous.sequence + 1:
        raise OrderStateTransitionError("order event sequence must be contiguous")
    if current.previous_status is not previous.status:
        raise OrderStateTransitionError("previous_status does not match prior event")
    if previous.status in TERMINAL_ORDER_STATUSES:
        raise OrderStateTransitionError("terminal order status is immutable")
    if current.status not in LEGAL_ORDER_TRANSITIONS[previous.status]:
        raise OrderStateTransitionError(
            f"illegal order transition: {previous.status.value} -> {current.status.value}"
        )


class OrderIntent(BaseModel):
    """不可變且 broker-neutral 的下單意圖與最小 provenance。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    intent_id: str
    correlation_id: str
    causation_id: str | None = None
    position_direction: PositionDirection
    position_effect: PositionEffect
    quantity: int = Field(gt=0)
    target_position_ref: str | None = None
    risk_decision_ref: str | None = None

    @field_validator("intent_id", "correlation_id", mode="before")
    @classmethod
    def normalize_required_ref(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                raise ValueError("reference must not be blank")
            return normalized
        return value

    @field_validator(
        "causation_id",
        "target_position_ref",
        "risk_decision_ref",
        mode="before",
    )
    @classmethod
    def normalize_optional_ref(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                raise ValueError("optional reference must not be blank")
            return normalized
        return value


class PositionEffectValidationError(ValueError):
    """OrderIntent 與預期部位或 mechanical order 不一致。"""


def validate_position_effect(
    intent: OrderIntent,
    expected: AccountPosition | None,
) -> None:
    """純驗證 position effect；不修改部位，也不送出 broker order。"""

    if expected is None:
        if intent.position_effect != PositionEffect.OPEN:
            raise PositionEffectValidationError(
                "FLAT position only permits OPEN"
            )
        return

    if intent.position_direction != expected.direction:
        raise PositionEffectValidationError(
            "opposite direction requires CLOSE, confirmed FLAT, then re-evaluation"
        )

    if intent.position_effect == PositionEffect.OPEN:
        return
    if intent.position_effect == PositionEffect.REDUCE:
        if intent.quantity >= expected.quantity:
            raise PositionEffectValidationError(
                "REDUCE quantity must be less than expected quantity"
            )
        return
    if intent.quantity != expected.quantity:
        raise PositionEffectValidationError(
            "CLOSE quantity must equal expected quantity"
        )


def validate_order_intent_consistency(
    *,
    order_direction: str,
    order_quantity: int,
    intent: OrderIntent,
) -> None:
    """驗證 legacy mechanical Order 與 canonical intent 的方向及數量一致。"""

    if order_quantity != intent.quantity:
        raise PositionEffectValidationError(
            "order quantity must equal intent quantity"
        )
    if order_direction != intent.position_direction.value:
        raise PositionEffectValidationError(
            "order direction must equal intent position direction"
        )
