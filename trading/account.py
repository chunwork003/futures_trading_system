from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PositionDirection(str, Enum):
    """Broker-neutral 實體部位方向。"""

    LONG = "LONG"
    SHORT = "SHORT"


class _BrokerAccountIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    broker: str
    account_ref: str

    @field_validator("broker", mode="before")
    @classmethod
    def normalize_broker(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("broker", "account_ref", mode="after")
    @classmethod
    def require_non_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("value must not be blank")
        return normalized


class BrokerAccount(_BrokerAccountIdentity):
    """不含憑證與 native SDK object 的 broker-neutral 帳戶識別。"""

    account_type: str | None = None
    display_name: str | None = None

    @field_validator("account_type", mode="before")
    @classmethod
    def normalize_account_type(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().upper()
            return normalized or None
        return value

    @field_validator("display_name", mode="before")
    @classmethod
    def normalize_display_name(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None
        return value


class AccountPosition(_BrokerAccountIdentity):
    """系統內部預期的實體帳戶部位；FLAT 以 absence 表示。"""

    instrument_id: int = Field(gt=0)
    contract_id: int | None = Field(default=None, gt=0)
    direction: PositionDirection
    quantity: int = Field(gt=0)


class BrokerPositionSnapshot(_BrokerAccountIdentity):
    """由 broker 觀察到的實際部位快照，不得覆寫內部預期狀態。"""

    instrument_id: int = Field(gt=0)
    contract_id: int | None = Field(default=None, gt=0)
    direction: PositionDirection
    quantity: int = Field(gt=0)
    observed_at: datetime
    average_price: Decimal | None = None

    @field_validator("observed_at")
    @classmethod
    def require_aware_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        return value


@runtime_checkable
class BrokerAccountProvider(Protocol):
    """唯讀 broker 帳戶查詢能力；不包含 execution 或 corrective action。"""

    def list_accounts(self) -> tuple[BrokerAccount, ...]: ...


@runtime_checkable
class BrokerPositionProvider(Protocol):
    """唯讀 broker 部位查詢能力；不包含 execution 或 corrective action。"""

    def list_positions(
        self, account: BrokerAccount
    ) -> tuple[BrokerPositionSnapshot, ...]: ...
