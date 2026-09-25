from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from trading.account import AccountPosition, PositionDirection


class PositionEffect(str, Enum):
    """OrderIntent 對既有實體部位的明確影響。"""

    OPEN = "OPEN"
    REDUCE = "REDUCE"
    CLOSE = "CLOSE"


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
