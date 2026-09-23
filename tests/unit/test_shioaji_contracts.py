from types import SimpleNamespace

import pytest

from backtest.shioaji_contracts import resolve_future_contract


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
