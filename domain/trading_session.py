from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, field_validator


class TradingSessionRef(BaseModel):
    """Broker-neutral 交易時段參照，供 domain model 指向版本化 calendar rule。"""

    session_ref: str
    exchange: str
    timezone: str
    rule_version: str

    @field_validator("session_ref", "rule_version")
    @classmethod
    def require_non_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("exchange")
    @classmethod
    def normalize_exchange(cls, value: str) -> str:
        value = value.strip().upper()
        if not value:
            raise ValueError("exchange must not be blank")
        return value

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("timezone must not be blank")
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as error:
            raise ValueError("timezone must be a valid IANA timezone") from error
        return value
