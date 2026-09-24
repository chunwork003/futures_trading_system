from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class ContractSeriesType(str, Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    WEEKLY = "WEEKLY"
    OTHER = "OTHER"


class ContractStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    INACTIVE = "INACTIVE"


class ContractSpec(BaseModel):
    """Broker-neutral 上市契約規格；canonical code 不等同 broker contract code。"""

    contract_id: int = Field(gt=0)
    instrument_id: int = Field(gt=0)
    canonical_code: str
    series_type: ContractSeriesType
    expiration_date: date | None = None
    contract_month: date | None = None
    listing_date: date | None = None
    last_trade_date: date | None = None
    settlement_date: date | None = None
    status: ContractStatus = ContractStatus.ACTIVE
    session_override_ref: str | None = None

    @field_validator("canonical_code")
    @classmethod
    def require_canonical_code(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("canonical_code must not be blank")
        return value

    @field_validator("series_type", "status", mode="before")
    @classmethod
    def normalize_enum_value(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("contract_month")
    @classmethod
    def validate_contract_month(cls, value: date | None) -> date | None:
        if value is not None and value.day != 1:
            raise ValueError("contract_month must use the first day of the month")
        return value

    @field_validator("session_override_ref")
    @classmethod
    def normalize_optional_reference(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def validate_lifecycle_dates(self) -> "ContractSpec":
        lifecycle_dates = (
            self.expiration_date,
            self.last_trade_date,
            self.settlement_date,
        )
        if self.listing_date is not None and any(
            value is not None and self.listing_date > value
            for value in lifecycle_dates
        ):
            raise ValueError("listing_date must not follow lifecycle end dates")
        if (
            self.last_trade_date is not None
            and self.settlement_date is not None
            and self.last_trade_date > self.settlement_date
        ):
            raise ValueError("last_trade_date must not follow settlement_date")
        return self


class Contract(BaseModel):
    contract_id: int
    instrument_id: int

    contract_code: str
    contract_month: date

    listing_date: Optional[date] = None
    last_trade_date: Optional[date] = None
    settlement_date: Optional[date] = None

    status: str = "ACTIVE"

    def to_spec(
        self,
        *,
        series_type: ContractSeriesType = ContractSeriesType.MONTHLY,
        expiration_date: date | None = None,
        session_override_ref: str | None = None,
    ) -> ContractSpec:
        """轉為 canonical spec；MONTHLY 僅是既有 contract_month 資料的相容假設。"""
        return ContractSpec(
            contract_id=self.contract_id,
            instrument_id=self.instrument_id,
            canonical_code=self.contract_code,
            series_type=series_type,
            expiration_date=expiration_date,
            contract_month=self.contract_month,
            listing_date=self.listing_date,
            last_trade_date=self.last_trade_date,
            settlement_date=self.settlement_date,
            status=self.status,
            session_override_ref=session_override_ref,
        )
