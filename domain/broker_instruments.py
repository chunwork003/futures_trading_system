from collections.abc import Iterable
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class BrokerInstrumentReference(BaseModel):
    """Canonical market identity 與外部 broker code 之間的 broker-neutral reference。"""

    model_config = ConfigDict(extra="forbid")

    broker: str
    instrument_id: int = Field(gt=0)
    contract_id: int | None = Field(default=None, gt=0)
    broker_product_code: str | None = None
    broker_contract_code: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None

    @field_validator("broker", mode="before")
    @classmethod
    def normalize_broker(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("broker")
    @classmethod
    def require_broker(cls, value: str) -> str:
        if not value:
            raise ValueError("broker must not be blank")
        return value

    @field_validator(
        "broker_product_code",
        "broker_contract_code",
        mode="before",
    )
    @classmethod
    def normalize_optional_code(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None
        return value

    @model_validator(mode="after")
    def validate_reference(self) -> "BrokerInstrumentReference":
        if self.broker_product_code is None and self.broker_contract_code is None:
            raise ValueError(
                "broker_product_code or broker_contract_code is required"
            )
        if (
            self.effective_from is not None
            and self.effective_to is not None
            and self.effective_from > self.effective_to
        ):
            raise ValueError("effective_from must not follow effective_to")
        return self


class BrokerInstrumentMappingError(ValueError):
    """Broker instrument mapping 無法安全解析。"""


class BrokerInstrumentMappingNotFound(BrokerInstrumentMappingError):
    """指定 canonical identity 找不到有效 broker mapping。"""


class AmbiguousBrokerInstrumentMapping(BrokerInstrumentMappingError):
    """指定日期存在多個有效 broker mapping。"""


class BrokerInstrumentResolver:
    """以 broker、canonical IDs 與有效日期解析唯一 mapping reference。"""

    def __init__(self, references: Iterable[BrokerInstrumentReference]):
        self._references = tuple(references)

    def resolve(
        self,
        *,
        broker: str,
        instrument_id: int,
        as_of_date: date,
        contract_id: int | None = None,
    ) -> BrokerInstrumentReference:
        normalized_broker = broker.strip().upper()
        if not normalized_broker:
            raise ValueError("broker must not be blank")
        if instrument_id <= 0:
            raise ValueError("instrument_id must be > 0")
        if contract_id is not None and contract_id <= 0:
            raise ValueError("contract_id must be > 0 when provided")

        matches = [
            reference
            for reference in self._references
            if reference.broker == normalized_broker
            and reference.instrument_id == instrument_id
            and reference.contract_id == contract_id
            and (
                reference.effective_from is None
                or reference.effective_from <= as_of_date
            )
            and (
                reference.effective_to is None
                or as_of_date <= reference.effective_to
            )
        ]

        if not matches:
            raise BrokerInstrumentMappingNotFound(
                "broker instrument mapping not found for "
                f"broker={normalized_broker}, instrument_id={instrument_id}, "
                f"contract_id={contract_id}, as_of_date={as_of_date}"
            )
        if len(matches) > 1:
            raise AmbiguousBrokerInstrumentMapping(
                "multiple broker instrument mappings are valid for "
                f"broker={normalized_broker}, instrument_id={instrument_id}, "
                f"contract_id={contract_id}, as_of_date={as_of_date}"
            )
        return matches[0]

    def resolve_by_broker_contract_code(
        self,
        *,
        broker: str,
        broker_contract_code: str,
        as_of_date: date,
    ) -> BrokerInstrumentReference:
        """以 case-sensitive native contract code 反查唯一 canonical listed contract。"""

        normalized_broker = broker.strip().upper()
        normalized_code = broker_contract_code.strip()
        if not normalized_broker:
            raise ValueError("broker must not be blank")
        if not normalized_code:
            raise ValueError("broker_contract_code must not be blank")

        matches = [
            reference
            for reference in self._references
            if reference.broker == normalized_broker
            and reference.contract_id is not None
            and reference.broker_contract_code == normalized_code
            and (
                reference.effective_from is None
                or reference.effective_from <= as_of_date
            )
            and (
                reference.effective_to is None
                or as_of_date <= reference.effective_to
            )
        ]
        if not matches:
            raise BrokerInstrumentMappingNotFound(
                "broker contract mapping not found for "
                f"broker={normalized_broker}, broker_contract_code={normalized_code}, "
                f"as_of_date={as_of_date}"
            )
        if len(matches) > 1:
            raise AmbiguousBrokerInstrumentMapping(
                "multiple broker contract mappings are valid for "
                f"broker={normalized_broker}, broker_contract_code={normalized_code}, "
                f"as_of_date={as_of_date}"
            )
        return matches[0]
