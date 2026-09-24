from collections.abc import Iterable
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class MarginScheduleEntry(BaseModel):
    """Broker-neutral、effective-dated margin reference；不代表 scenario override 或 broker snapshot。"""

    margin_id: int = Field(gt=0)
    instrument_id: int = Field(gt=0)
    contract_id: int | None = Field(default=None, gt=0)
    effective_date: date
    currency: str
    clearing_margin: Decimal = Field(ge=0)
    maintenance_margin: Decimal = Field(ge=0)
    initial_margin: Decimal = Field(ge=0)
    source: str
    published_at: datetime | None = None

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        if len(value) != 3 or not value.isascii() or not value.isalpha():
            raise ValueError("currency must be a three-letter ASCII alphabetic code")
        return value

    @field_validator("source")
    @classmethod
    def require_source(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("source must not be blank")
        return value

    @field_validator("published_at")
    @classmethod
    def require_aware_published_at(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is not None and value.utcoffset() is None:
            raise ValueError("published_at must be timezone-aware")
        return value


class AmbiguousMarginScheduleError(ValueError):
    """同一 canonical margin natural key 出現重複資料。"""


class MarginScheduleResolver:
    """依 effective date 解析 canonical margin，不套用 scenario 或 broker fallback。"""

    def __init__(self, entries: Iterable[MarginScheduleEntry]):
        self._entries = tuple(entries)
        self._validate_unique_schedule_keys()

    def resolve(
        self,
        *,
        instrument_id: int,
        as_of_date: date,
        contract_id: int | None = None,
    ) -> MarginScheduleEntry | None:
        if instrument_id <= 0:
            raise ValueError("instrument_id must be > 0")
        if contract_id is not None and contract_id <= 0:
            raise ValueError("contract_id must be > 0 when provided")

        if contract_id is not None:
            contract_entry = self._latest_entry(
                instrument_id=instrument_id,
                contract_id=contract_id,
                as_of_date=as_of_date,
            )
            if contract_entry is not None:
                return contract_entry

        return self._latest_entry(
            instrument_id=instrument_id,
            contract_id=None,
            as_of_date=as_of_date,
        )

    def _latest_entry(
        self,
        *,
        instrument_id: int,
        contract_id: int | None,
        as_of_date: date,
    ) -> MarginScheduleEntry | None:
        candidates = (
            entry
            for entry in self._entries
            if entry.instrument_id == instrument_id
            and entry.contract_id == contract_id
            and entry.effective_date <= as_of_date
        )
        return max(
            candidates,
            key=lambda entry: entry.effective_date,
            default=None,
        )

    def _validate_unique_schedule_keys(self) -> None:
        seen: set[tuple[int, int | None, date]] = set()
        for entry in self._entries:
            key = (
                entry.instrument_id,
                entry.contract_id,
                entry.effective_date,
            )
            if key in seen:
                raise AmbiguousMarginScheduleError(
                    "duplicate margin schedule entry for "
                    f"instrument_id={entry.instrument_id}, "
                    f"contract_id={entry.contract_id}, "
                    f"effective_date={entry.effective_date}"
                )
            seen.add(key)
