from __future__ import annotations

from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    model_validator,
)

from trading.account import AccountPosition, BrokerPositionSnapshot


class ReconciliationStatus(str, Enum):
    """Pairwise reconciliation 的完整、固定狀態集合。"""

    MATCH = "MATCH"
    INTERNAL_ONLY = "INTERNAL_ONLY"
    BROKER_ONLY = "BROKER_ONLY"
    CONTRACT_MISMATCH = "CONTRACT_MISMATCH"
    DIRECTION_MISMATCH = "DIRECTION_MISMATCH"
    QUANTITY_MISMATCH = "QUANTITY_MISMATCH"
    UNKNOWN_EXTERNAL_STATE = "UNKNOWN_EXTERNAL_STATE"


class PositionComparisonError(ValueError):
    """兩個 position identity 不屬於同一個可比較 pair。"""


class ReconciliationResult(BaseModel):
    """不可變的比較證據；只描述結果，不覆寫狀態或執行修正。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: ReconciliationStatus
    expected: AccountPosition | None
    actual: BrokerPositionSnapshot | None
    evidence: tuple[str, ...] = ()

    @field_validator("evidence", mode="before")
    @classmethod
    def normalize_evidence(cls, value: object) -> object:
        if isinstance(value, (list, tuple)):
            normalized: list[str] = []
            for item in value:
                if not isinstance(item, str):
                    normalized.append(item)
                    continue
                stripped = item.strip()
                if not stripped:
                    raise ValueError("evidence item must not be blank")
                normalized.append(stripped)
            return tuple(normalized)
        return value

    @model_validator(mode="after")
    def validate_unknown_external_state(self) -> "ReconciliationResult":
        if self.status != ReconciliationStatus.UNKNOWN_EXTERNAL_STATE:
            return self
        if not self.evidence:
            raise ValueError("UNKNOWN_EXTERNAL_STATE requires evidence")
        if self.actual is not None:
            raise ValueError("UNKNOWN_EXTERNAL_STATE actual must be None")
        return self


class ExternalStateUnknownError(RuntimeError):
    """Broker external observation 無法安全取得或 canonicalize 的明確契約。"""


class ReconciliationPolicy(str, Enum):
    """Mismatch 的處理權限；不代表自動採用或自動修復。"""

    STRICT_HALT = "STRICT_HALT"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    BROKER_AUTHORITATIVE = "BROKER_AUTHORITATIVE"
    INTERNAL_AUTHORITATIVE = "INTERNAL_AUTHORITATIVE"


class ReconciliationCaseState(str, Enum):
    """人工或受控流程中的 reconciliation case lifecycle。"""

    HALT = "HALT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    RESOLVED = "RESOLVED"


class ReconciliationCaseError(ValueError):
    """Case 建立或狀態轉移違反 frozen reconciliation contract。"""


class ReconciliationCase(BaseModel):
    """不可變的 mismatch case；不含 persistence、broker action 或 hidden time。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str
    result: ReconciliationResult
    policy: ReconciliationPolicy
    state: ReconciliationCaseState
    resolution_note: str | None = None

    @field_validator("case_id", mode="before")
    @classmethod
    def normalize_case_id(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                raise ValueError("case_id must not be blank")
            return normalized
        return value

    @field_validator("resolution_note", mode="before")
    @classmethod
    def normalize_resolution_note(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                raise ValueError("resolution_note must not be blank")
            return normalized
        return value

    @model_validator(mode="after")
    def validate_resolution_state(self) -> "ReconciliationCase":
        if self.state == ReconciliationCaseState.RESOLVED:
            if self.resolution_note is None:
                raise ValueError("RESOLVED case requires resolution_note")
        elif self.resolution_note is not None:
            raise ValueError(
                "HALT or REVIEW_REQUIRED case must not have resolution_note"
            )
        return self


def create_reconciliation_case(
    *,
    case_id: str,
    result: ReconciliationResult,
    policy: ReconciliationPolicy,
) -> ReconciliationCase:
    """依 policy 建立純 mismatch case；MATCH 不產生 case。"""

    if result.status == ReconciliationStatus.MATCH:
        raise ReconciliationCaseError("MATCH result cannot create a case")
    state = (
        ReconciliationCaseState.HALT
        if policy == ReconciliationPolicy.STRICT_HALT
        else ReconciliationCaseState.REVIEW_REQUIRED
    )
    return ReconciliationCase(
        case_id=case_id,
        result=result,
        policy=policy,
        state=state,
    )


def resolve_reconciliation_case(
    case: ReconciliationCase,
    *,
    resolution_note: str,
) -> ReconciliationCase:
    """以明確說明建立新的 RESOLVED case；不修改原 case 或交易狀態。"""

    if case.state == ReconciliationCaseState.RESOLVED:
        raise ReconciliationCaseError("RESOLVED case cannot be resolved again")
    normalized_note = resolution_note.strip()
    if not normalized_note:
        raise ReconciliationCaseError("resolution_note must not be blank")
    return ReconciliationCase(
        case_id=case.case_id,
        result=case.result,
        policy=case.policy,
        state=ReconciliationCaseState.RESOLVED,
        resolution_note=normalized_note,
    )


def compare_positions(
    expected: AccountPosition | None,
    actual: BrokerPositionSnapshot | None,
) -> ReconciliationResult:
    """依固定 precedence 比較一組 expected / actual position。"""

    if expected is None and actual is None:
        status = ReconciliationStatus.MATCH
    elif expected is not None and actual is None:
        status = ReconciliationStatus.INTERNAL_ONLY
    elif expected is None:
        status = ReconciliationStatus.BROKER_ONLY
    else:
        identity_expected = (
            expected.broker,
            expected.account_ref,
            expected.instrument_id,
        )
        identity_actual = (
            actual.broker,
            actual.account_ref,
            actual.instrument_id,
        )
        if identity_expected != identity_actual:
            raise PositionComparisonError(
                "expected and actual positions do not share broker/account/instrument identity"
            )
        if expected.contract_id != actual.contract_id:
            status = ReconciliationStatus.CONTRACT_MISMATCH
        elif expected.direction != actual.direction:
            status = ReconciliationStatus.DIRECTION_MISMATCH
        elif expected.quantity != actual.quantity:
            status = ReconciliationStatus.QUANTITY_MISMATCH
        else:
            status = ReconciliationStatus.MATCH

    return ReconciliationResult(status=status, expected=expected, actual=actual)
