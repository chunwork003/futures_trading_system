from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict

from trading.account import AccountPosition, BrokerPositionSnapshot


class ReconciliationStatus(str, Enum):
    MATCH = "MATCH"
    INTERNAL_ONLY = "INTERNAL_ONLY"
    BROKER_ONLY = "BROKER_ONLY"
    CONTRACT_MISMATCH = "CONTRACT_MISMATCH"
    DIRECTION_MISMATCH = "DIRECTION_MISMATCH"
    QUANTITY_MISMATCH = "QUANTITY_MISMATCH"


class PositionComparisonError(ValueError):
    """兩個 position identity 不屬於同一個可比較 pair。"""


class ReconciliationResult(BaseModel):
    """純比較結果；只描述 mismatch，不執行修正。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: ReconciliationStatus
    expected: AccountPosition | None
    actual: BrokerPositionSnapshot | None


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
