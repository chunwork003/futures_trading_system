from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest

from adapters.sinopac.account_mapping import (
    SinopacAccountMappingError,
    map_sinopac_account,
    map_sinopac_future_position,
)
from domain.broker_instruments import (
    BrokerInstrumentMappingNotFound,
    BrokerInstrumentReference,
    BrokerInstrumentResolver,
)
from trading.account import PositionDirection


def _native_account(account_type: str = "F") -> SimpleNamespace:
    return SimpleNamespace(
        account_type=account_type,
        broker_id="9A95",
        account_id="1234567",
        signed=True,
        username="private-user",
        person_id="A123456789",
    )


def _resolver() -> BrokerInstrumentResolver:
    return BrokerInstrumentResolver(
        [
            BrokerInstrumentReference(
                broker="SINOPAC",
                instrument_id=1,
                contract_id=101,
                broker_contract_code="TX-synthetic-202610",
                effective_from=date(2026, 9, 1),
            )
        ]
    )


def test_account_mapping_uses_opaque_reference_without_pii() -> None:
    account = map_sinopac_account(_native_account())

    assert account.broker == "SINOPAC"
    assert account.account_ref == "9A95-1234567"
    assert account.account_type == "FUTURES_OPTIONS"
    serialized = account.model_dump()
    assert "person_id" not in serialized
    assert "username" not in serialized


@pytest.mark.parametrize(
    ("native_type", "canonical"),
    [("F", "FUTURES_OPTIONS"), ("S", "SECURITIES"), ("H", "INTERNATIONAL")],
)
def test_approved_account_type_mapping(
    native_type: str, canonical: str
) -> None:
    assert map_sinopac_account(_native_account(native_type)).account_type == canonical


def test_unknown_account_type_is_explicit() -> None:
    with pytest.raises(SinopacAccountMappingError, match="unsupported"):
        map_sinopac_account(_native_account("UNKNOWN"))


@pytest.mark.parametrize(
    ("native_direction", "canonical"),
    [("Buy", PositionDirection.LONG), ("Sell", PositionDirection.SHORT)],
)
def test_future_position_mapping_is_pure_and_deterministic(
    native_direction: str,
    canonical: PositionDirection,
) -> None:
    account = map_sinopac_account(_native_account())
    observed_at = datetime(2026, 9, 25, 9, 0, tzinfo=timezone.utc)
    native_position = SimpleNamespace(
        code="TX-synthetic-202610",
        direction=native_direction,
        quantity=2,
        price=20123.4,
        last_price=20125,
        pnl=100,
    )

    snapshot = map_sinopac_future_position(
        native_position,
        account=account,
        resolver=_resolver(),
        observed_at=observed_at,
        as_of_date=date(2026, 9, 25),
    )

    assert snapshot.instrument_id == 1
    assert snapshot.contract_id == 101
    assert snapshot.direction == canonical
    assert snapshot.quantity == 2
    assert snapshot.average_price == Decimal("20123.4")
    assert snapshot.observed_at is observed_at
    assert "last_price" not in snapshot.model_dump()
    assert "pnl" not in snapshot.model_dump()


def test_unknown_direction_and_contract_are_explicit() -> None:
    account = map_sinopac_account(_native_account())
    common = {
        "account": account,
        "resolver": _resolver(),
        "observed_at": datetime.now(timezone.utc),
        "as_of_date": date(2026, 9, 25),
    }
    with pytest.raises(SinopacAccountMappingError, match="direction"):
        map_sinopac_future_position(
            SimpleNamespace(code="TX-synthetic-202610", direction="Flat", quantity=1, price=1),
            **common,
        )
    with pytest.raises(BrokerInstrumentMappingNotFound):
        map_sinopac_future_position(
            SimpleNamespace(code="UNKNOWN", direction="Buy", quantity=1, price=1),
            **common,
        )


def test_position_mapping_rejects_non_futures_account() -> None:
    with pytest.raises(SinopacAccountMappingError, match="futures/options"):
        map_sinopac_future_position(
            SimpleNamespace(code="X", direction="Buy", quantity=1, price=1),
            account=map_sinopac_account(_native_account("S")),
            resolver=_resolver(),
            observed_at=datetime.now(timezone.utc),
            as_of_date=date(2026, 9, 25),
        )
