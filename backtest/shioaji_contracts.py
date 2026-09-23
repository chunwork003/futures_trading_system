from __future__ import annotations

from typing import Any


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
