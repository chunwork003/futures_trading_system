from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from domain.broker_instruments import BrokerInstrumentResolver
from trading.account import (
    BrokerAccount,
    BrokerPositionSnapshot,
    PositionDirection,
)


class SinopacAccountMappingError(ValueError):
    """Sinopac native observation 無法依核准語意安全映射。"""


_ACCOUNT_TYPES = {
    "F": "FUTURES_OPTIONS",
    "S": "SECURITIES",
    "H": "INTERNATIONAL",
}

_DIRECTIONS = {
    "Buy": PositionDirection.LONG,
    "Sell": PositionDirection.SHORT,
}


def _native_value(value: Any) -> Any:
    return getattr(value, "value", value)


def map_sinopac_account(native_account: object) -> BrokerAccount:
    """只取 approved identity fields，避免 PII 與 native object 洩漏至 core。"""

    try:
        native_type = str(_native_value(getattr(native_account, "account_type")))
        broker_id = str(getattr(native_account, "broker_id")).strip()
        account_id = str(getattr(native_account, "account_id")).strip()
    except AttributeError as exc:
        raise SinopacAccountMappingError("native account identity is incomplete") from exc

    account_type = _ACCOUNT_TYPES.get(native_type)
    if account_type is None:
        raise SinopacAccountMappingError(
            f"unsupported Sinopac account type: {native_type}"
        )
    if not broker_id or not account_id:
        raise SinopacAccountMappingError("broker_id and account_id are required")

    return BrokerAccount(
        broker="SINOPAC",
        account_ref=f"{broker_id}-{account_id}",
        account_type=account_type,
    )


def map_sinopac_future_position(
    native_position: object,
    *,
    account: BrokerAccount,
    resolver: BrokerInstrumentResolver,
    observed_at: datetime,
    as_of_date: date,
) -> BrokerPositionSnapshot:
    """將單一 Shioaji FuturePosition 純映射為 canonical actual snapshot。"""

    if account.broker != "SINOPAC" or account.account_type != "FUTURES_OPTIONS":
        raise SinopacAccountMappingError(
            "future position mapping requires a SINOPAC futures/options account"
        )
    try:
        broker_code = str(getattr(native_position, "code")).strip()
        native_direction = str(_native_value(getattr(native_position, "direction")))
        quantity = int(getattr(native_position, "quantity"))
        price = getattr(native_position, "price")
    except (AttributeError, TypeError, ValueError) as exc:
        raise SinopacAccountMappingError("native future position is invalid") from exc

    direction = _DIRECTIONS.get(native_direction)
    if direction is None:
        raise SinopacAccountMappingError(
            f"unsupported Sinopac position direction: {native_direction}"
        )
    if not broker_code:
        raise SinopacAccountMappingError("broker contract code is required")

    reference = resolver.resolve_by_broker_contract_code(
        broker="SINOPAC",
        broker_contract_code=broker_code,
        as_of_date=as_of_date,
    )
    return BrokerPositionSnapshot(
        broker=account.broker,
        account_ref=account.account_ref,
        instrument_id=reference.instrument_id,
        contract_id=reference.contract_id,
        direction=direction,
        quantity=quantity,
        observed_at=observed_at,
        average_price=Decimal(str(price)),
    )
