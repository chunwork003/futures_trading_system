from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class AssetType(str, Enum):
    FUTURE = "FUTURES"
    STOCK = "STOCK"
    ETF = "ETF"
    INDEX = "INDEX"


class InstrumentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class InstrumentSpec(BaseModel):
    """Broker-neutral canonical instrument specification，供回測、模擬與交易 runtime 共用。"""

    instrument_id: int = Field(gt=0)
    canonical_symbol: str
    name: str
    asset_type: AssetType
    exchange: str
    currency: str = "TWD"
    multiplier: Decimal | None = Field(default=None, gt=0)
    tick_size: Decimal | None = Field(default=None, gt=0)
    trading_session_ref: str | None = None
    status: InstrumentStatus = InstrumentStatus.ACTIVE

    @field_validator("canonical_symbol", "exchange", mode="before")
    @classmethod
    def normalize_identifier(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip().upper()
        return value

    @field_validator("canonical_symbol", "name", "exchange")
    @classmethod
    def require_non_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("asset_type", mode="before")
    @classmethod
    def normalize_asset_type(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().upper()
            if normalized == "FUTURE":
                return AssetType.FUTURE.value
            return normalized
        return value

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip().upper()
        return value

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        if len(value) != 3 or not value.isascii() or not value.isalpha():
            raise ValueError("currency must be a three-letter ASCII alphabetic code")
        return value

    @field_validator("trading_session_ref")
    @classmethod
    def normalize_optional_reference(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @property
    def linear_tick_value(self) -> Decimal | None:
        """線性商品每跳價值；規格不足時回傳 None，不推測缺失值。"""
        if self.multiplier is None or self.tick_size is None:
            return None
        return self.multiplier * self.tick_size


class Instrument(BaseModel):
    instrument_id: int
    symbol: str
    name: str
    asset_type: str
    exchange: str
    currency: str = "TWD"
    multiplier: Optional[float] = None
    tick_size: Optional[float] = None

    def to_spec(
        self,
        *,
        trading_session_ref: str | None = None,
        status: InstrumentStatus = InstrumentStatus.ACTIVE,
    ) -> InstrumentSpec:
        """將既有資料模型轉為 canonical specification，保留舊 import 與欄位。"""
        return InstrumentSpec(
            instrument_id=self.instrument_id,
            canonical_symbol=self.symbol,
            name=self.name,
            asset_type=self.asset_type,
            exchange=self.exchange,
            currency=self.currency,
            multiplier=(
                Decimal(str(self.multiplier))
                if self.multiplier is not None
                else None
            ),
            tick_size=(
                Decimal(str(self.tick_size))
                if self.tick_size is not None
                else None
            ),
            trading_session_ref=trading_session_ref,
            status=status,
        )
