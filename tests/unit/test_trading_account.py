from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from trading.account import (
    AccountPosition,
    BrokerAccount,
    BrokerAccountProvider,
    BrokerPositionProvider,
    BrokerPositionSnapshot,
    PositionDirection,
)


def test_broker_account_normalizes_identity_and_metadata() -> None:
    account = BrokerAccount(
        broker=" sinopac ",
        account_ref=" 9A95-1234567 ",
        account_type=" futures_options ",
        display_name="  Primary  ",
    )

    assert account.broker == "SINOPAC"
    assert account.account_ref == "9A95-1234567"
    assert account.account_type == "FUTURES_OPTIONS"
    assert account.display_name == "Primary"


@pytest.mark.parametrize("field", ["broker", "account_ref"])
def test_broker_account_rejects_blank_identity(field: str) -> None:
    values = {"broker": "SINOPAC", "account_ref": "9A95-1234567"}
    values[field] = "  "
    with pytest.raises(ValidationError, match="must not be blank"):
        BrokerAccount(**values)


def test_models_forbid_native_or_secret_fields() -> None:
    with pytest.raises(ValidationError, match="password"):
        BrokerAccount(
            broker="SINOPAC",
            account_ref="9A95-1234567",
            password="secret",
        )
    with pytest.raises(ValidationError, match="native_position"):
        BrokerPositionSnapshot(
            broker="SINOPAC",
            account_ref="9A95-1234567",
            instrument_id=1,
            contract_id=101,
            direction=PositionDirection.LONG,
            quantity=1,
            observed_at=datetime.now(timezone.utc),
            native_position=object(),
        )


def test_expected_and_actual_models_are_distinct_and_immutable() -> None:
    expected = AccountPosition(
        broker="SINOPAC",
        account_ref="9A95-1234567",
        instrument_id=1,
        contract_id=101,
        direction=PositionDirection.LONG,
        quantity=2,
    )
    actual = BrokerPositionSnapshot(
        **expected.model_dump(),
        observed_at=datetime.now(timezone.utc),
        average_price=Decimal("20123.5"),
    )

    assert type(expected) is not type(actual)
    assert actual.average_price == Decimal("20123.5")
    with pytest.raises(ValidationError):
        expected.quantity = 3


def test_position_quantity_must_be_positive_and_flat_is_absence() -> None:
    with pytest.raises(ValidationError):
        AccountPosition(
            broker="SINOPAC",
            account_ref="9A95-1234567",
            instrument_id=1,
            contract_id=101,
            direction=PositionDirection.LONG,
            quantity=0,
        )


def test_snapshot_requires_timezone_aware_observed_at() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        BrokerPositionSnapshot(
            broker="SINOPAC",
            account_ref="9A95-1234567",
            instrument_id=1,
            contract_id=101,
            direction=PositionDirection.LONG,
            quantity=1,
            observed_at=datetime(2026, 9, 25, 9, 0),
        )


def test_query_ports_are_read_only_capabilities() -> None:
    assert "list_accounts" in BrokerAccountProvider.__dict__
    assert "list_positions" in BrokerPositionProvider.__dict__
    for forbidden in ("submit_order", "cancel_order", "repair"):
        assert forbidden not in BrokerAccountProvider.__dict__
        assert forbidden not in BrokerPositionProvider.__dict__
