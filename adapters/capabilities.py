from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class BrokerCapability(str, Enum):
    """Broker-neutral 能力識別；供 adapter 證據矩陣與上游顯式檢查共用。"""

    ACCOUNT_QUERY = "ACCOUNT_QUERY"
    POSITION_QUERY = "POSITION_QUERY"
    ORDER_PLACE = "ORDER_PLACE"
    ORDER_UPDATE = "ORDER_UPDATE"
    ORDER_CANCEL = "ORDER_CANCEL"
    ORDER_STATUS = "ORDER_STATUS"
    TRADE_LIST = "TRADE_LIST"
    ORDER_DEAL_EVENT = "ORDER_DEAL_EVENT"


class BrokerCapabilitySupport(str, Enum):
    """能力的已知支援狀態；UNKNOWN 不得被當成支援或驗證完成。"""

    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    UNKNOWN = "UNKNOWN"


class BrokerVerificationMode(str, Enum):
    """互不隱含的驗證方式；文件、模擬與 production 證據不可互相替代。"""

    DOCUMENTATION = "DOCUMENTATION"
    FAKE = "FAKE"
    SIMULATION = "SIMULATION"
    PRODUCTION = "PRODUCTION"


class BrokerCapabilityEvidence(BaseModel):
    """保存單一 broker 能力的可追溯證據，不執行操作亦不授權 LIVE。"""

    model_config = ConfigDict(frozen=True, extra="forbid")

    capability: BrokerCapability
    support: BrokerCapabilitySupport
    source_ids: tuple[str, ...]
    verification_modes: tuple[BrokerVerificationMode, ...]
    sdk_version: str | None
    verified_on: date
    note: str | None = None

    @field_validator("source_ids")
    @classmethod
    def _normalize_source_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(item.strip() for item in value)
        if any(not item for item in normalized):
            raise ValueError("source_ids must contain non-blank values")
        if len(set(normalized)) != len(normalized):
            raise ValueError("source_ids must not contain duplicates")
        return normalized

    @field_validator("verification_modes")
    @classmethod
    def _normalize_verification_modes(
        cls, value: tuple[BrokerVerificationMode, ...]
    ) -> tuple[BrokerVerificationMode, ...]:
        if len(set(value)) != len(value):
            raise ValueError("verification_modes must not contain duplicates")
        order = {mode: index for index, mode in enumerate(BrokerVerificationMode)}
        return tuple(sorted(value, key=order.__getitem__))

    @field_validator("sdk_version", "note")
    @classmethod
    def _normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("optional text must be non-blank when provided")
        return normalized

    @model_validator(mode="after")
    def _validate_evidence_contract(self) -> BrokerCapabilityEvidence:
        if self.support in {
            BrokerCapabilitySupport.SUPPORTED,
            BrokerCapabilitySupport.UNSUPPORTED,
        } and not self.source_ids:
            raise ValueError("supported or unsupported capability requires source evidence")
        if (
            self.support is BrokerCapabilitySupport.UNKNOWN
            and self.verification_modes
        ):
            raise ValueError("unknown capability cannot claim verification modes")
        return self


class BrokerCapabilityMatrix(BaseModel):
    """Broker 能力證據集合；只供查詢與安全 gate，不具有執行權限。"""

    model_config = ConfigDict(frozen=True, extra="forbid")

    broker: str
    entries: tuple[BrokerCapabilityEvidence, ...]

    @field_validator("broker")
    @classmethod
    def _normalize_broker(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("broker must be non-blank")
        return normalized

    @field_validator("entries")
    @classmethod
    def _normalize_entries(
        cls, value: tuple[BrokerCapabilityEvidence, ...]
    ) -> tuple[BrokerCapabilityEvidence, ...]:
        capabilities = [entry.capability for entry in value]
        if len(set(capabilities)) != len(capabilities):
            raise ValueError("entries must not contain duplicate capabilities")
        order = {
            capability: index for index, capability in enumerate(BrokerCapability)
        }
        return tuple(sorted(value, key=lambda entry: order[entry.capability]))


class BrokerCapabilityUnavailableError(RuntimeError):
    """所需能力不存在、不支援或缺少指定驗證證據時的明確失敗。"""


def get_broker_capability(
    matrix: BrokerCapabilityMatrix,
    capability: BrokerCapability,
) -> BrokerCapabilityEvidence | None:
    """純查詢單一能力；缺少 entry 時回傳 None，不做任何 fallback。"""

    return next(
        (entry for entry in matrix.entries if entry.capability is capability),
        None,
    )


def require_broker_capability(
    matrix: BrokerCapabilityMatrix,
    capability: BrokerCapability,
    *,
    required_mode: BrokerVerificationMode | None = None,
) -> BrokerCapabilityEvidence:
    """顯式驗證能力與指定證據；不推導 LIVE 權限，也不執行 broker action。"""

    evidence = get_broker_capability(matrix, capability)
    if evidence is None:
        raise BrokerCapabilityUnavailableError(
            f"{matrix.broker} capability is missing: {capability.value}"
        )
    if evidence.support is BrokerCapabilitySupport.UNSUPPORTED:
        raise BrokerCapabilityUnavailableError(
            f"{matrix.broker} capability is unsupported: {capability.value}"
        )
    if evidence.support is BrokerCapabilitySupport.UNKNOWN:
        raise BrokerCapabilityUnavailableError(
            f"{matrix.broker} capability support is unknown: {capability.value}"
        )
    if required_mode is not None and required_mode not in evidence.verification_modes:
        raise BrokerCapabilityUnavailableError(
            f"{matrix.broker} capability {capability.value} lacks "
            f"{required_mode.value} verification"
        )
    return evidence
