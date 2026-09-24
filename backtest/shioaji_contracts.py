from __future__ import annotations

from typing import Any

from domain.broker_instruments import BrokerInstrumentReference


def resolve_future_contract(
    contracts: Any,
    contract_code: str,
) -> Any:
    if not contract_code:
        raise ValueError("contract_code is required")

    contract = contracts[contract_code]

    if contract is None:
        raise ValueError(
            f"Shioaji futures contract not found: {contract_code}"
        )

    return contract


def resolve_future_contract_reference(
    contracts: Any,
    reference: BrokerInstrumentReference,
) -> Any:
    """以 SINOPAC reference 的 listed-contract code 沿用既有 native lookup。"""
    if reference.broker != "SINOPAC":
        raise ValueError("broker reference must be SINOPAC")
    if reference.broker_contract_code is None:
        raise ValueError("broker_contract_code is required for native lookup")

    return resolve_future_contract(
        contracts,
        reference.broker_contract_code,
    )
