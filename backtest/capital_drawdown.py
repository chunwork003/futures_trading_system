from __future__ import annotations


def calculate_capital_drawdown(
    equity: float,
    reference_equity: float,
) -> float:
    if equity <= 0:
        raise ValueError("equity must be greater than zero")

    if reference_equity <= 0:
        raise ValueError("reference_equity must be greater than zero")

    if equity >= reference_equity:
        return 0.0

    return (reference_equity - equity) / reference_equity
