from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from persistence.contracts import normalize_aware_utc, normalize_stable_id
from trading.account import AccountPosition, BrokerPositionSnapshot
from trading.execution import Fill, OrderIntent, PositionEffect, PositionEffectValidationError


class AccountPositionSnapshot(BaseModel):
    """完整 expected-position batch；空 positions 明確代表 FLAT collection。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    snapshot_id: str
    broker: str
    account_ref: str
    effective_at: datetime
    recorded_at: datetime
    source_event_id: str
    positions: tuple[AccountPosition, ...]

    @field_validator("snapshot_id", "account_ref", "source_event_id", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("broker", mode="before")
    @classmethod
    def _broker(cls, value: object) -> object:
        return normalize_stable_id(value).upper() if isinstance(value, str) else value

    @field_validator("effective_at", "recorded_at")
    @classmethod
    def _utc(cls, value: datetime) -> datetime: return normalize_aware_utc(value)

    @model_validator(mode="after")
    def _scope(self) -> "AccountPositionSnapshot":
        if any(p.broker != self.broker or p.account_ref != self.account_ref for p in self.positions):
            raise ValueError("expected positions must match snapshot account scope")
        return self


class BrokerPositionObservation(BaseModel):
    """完整 broker actual observation batch；僅供 audit，不是 startup actual authority。"""

    model_config = ConfigDict(extra="forbid", frozen=True)
    observation_id: str
    broker: str
    account_ref: str
    observed_at: datetime
    recorded_at: datetime
    positions: tuple[BrokerPositionSnapshot, ...]

    @field_validator("observation_id", "account_ref", mode="before")
    @classmethod
    def _ids(cls, value: object) -> object:
        return normalize_stable_id(value) if isinstance(value, str) else value

    @field_validator("broker", mode="before")
    @classmethod
    def _broker(cls, value: object) -> object:
        return normalize_stable_id(value).upper() if isinstance(value, str) else value

    @field_validator("observed_at", "recorded_at")
    @classmethod
    def _utc(cls, value: datetime) -> datetime: return normalize_aware_utc(value)

    @model_validator(mode="after")
    def _scope(self) -> "BrokerPositionObservation":
        if any(
            p.broker != self.broker or p.account_ref != self.account_ref or p.observed_at != self.observed_at
            for p in self.positions
        ):
            raise ValueError("broker positions must match observation scope and observed_at")
        return self


@runtime_checkable
class ExpectedPositionSnapshotRepository(Protocol):
    def append(self, snapshot: AccountPositionSnapshot) -> None: ...
    def latest(self, broker: str, account_ref: str) -> AccountPositionSnapshot | None: ...
    def as_of(self, broker: str, account_ref: str, at: datetime) -> AccountPositionSnapshot | None: ...


@runtime_checkable
class BrokerPositionObservationRepository(Protocol):
    def append(self, observation: BrokerPositionObservation) -> None: ...


def project_expected_position(
    expected: AccountPosition | None,
    *,
    intent: OrderIntent,
    fill: Fill,
    broker: str,
    account_ref: str,
    instrument_id: int,
    contract_id: int | None,
) -> AccountPosition | None:
    """以 actual Fill quantity 投影 expected physical position；禁止 silent reversal。"""

    if fill.quantity <= 0:
        raise PositionEffectValidationError("fill quantity must be positive")
    if expected is None:
        if intent.position_effect is not PositionEffect.OPEN:
            raise PositionEffectValidationError("FLAT expected position only permits OPEN fill")
        return AccountPosition(
            broker=broker, account_ref=account_ref, instrument_id=instrument_id,
            contract_id=contract_id, direction=intent.position_direction, quantity=fill.quantity,
        )
    identity = (expected.broker, expected.account_ref, expected.instrument_id, expected.contract_id)
    if identity != (broker.upper(), account_ref, instrument_id, contract_id):
        raise PositionEffectValidationError("expected position identity mismatch")
    if expected.direction is not intent.position_direction:
        raise PositionEffectValidationError("opposite fill requires confirmed FLAT before OPEN")
    if intent.position_effect is PositionEffect.OPEN:
        quantity = expected.quantity + fill.quantity
    else:
        quantity = expected.quantity - fill.quantity
        if quantity < 0:
            raise PositionEffectValidationError("fill exceeds expected quantity")
        if intent.position_effect is PositionEffect.REDUCE and quantity <= 0:
            raise PositionEffectValidationError("REDUCE must leave a positive position")
        if intent.position_effect is PositionEffect.CLOSE and quantity > 0:
            return expected.model_copy(update={"quantity": quantity})
        if quantity == 0:
            return None
    return expected.model_copy(update={"quantity": quantity})
