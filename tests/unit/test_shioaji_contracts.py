from types import SimpleNamespace

import pytest

from backtest.shioaji_contracts import (
    resolve_future_contract,
    resolve_future_contract_reference,
)
from domain.broker_instruments import BrokerInstrumentReference


def test_resolve_future_contract():
    expected = SimpleNamespace(code="TXF202601")

    class Contracts:
        def __getitem__(self, code):
            return expected if code == "TXF202601" else None

    result = resolve_future_contract(
        Contracts(),
        "TXF202601",
    )

    assert result is expected


def test_resolve_future_contract_requires_code():
    with pytest.raises(ValueError, match="contract_code is required"):
        resolve_future_contract({}, "")


def test_resolve_future_contract_rejects_missing_contract():
    class Contracts:
        def __getitem__(self, code):
            return None

    with pytest.raises(ValueError, match="contract not found"):
        resolve_future_contract(Contracts(), "TXF202601")


def test_resolve_future_contract_reference_uses_existing_lookup():
    expected = SimpleNamespace(code="Tx-Synthetic-202601")

    class Contracts:
        def __getitem__(self, code):
            return expected if code == "Tx-Synthetic-202601" else None

    reference = BrokerInstrumentReference(
        broker="sinopac",
        instrument_id=1,
        contract_id=101,
        broker_product_code="TXF",
        broker_contract_code="Tx-Synthetic-202601",
    )

    result = resolve_future_contract_reference(Contracts(), reference)

    assert result is expected


def test_resolve_future_contract_reference_requires_listed_contract_code():
    reference = BrokerInstrumentReference(
        broker="SINOPAC",
        instrument_id=1,
        broker_product_code="TXF",
    )

    with pytest.raises(ValueError, match="broker_contract_code is required"):
        resolve_future_contract_reference({}, reference)
