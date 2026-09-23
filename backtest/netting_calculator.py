from __future__ import annotations

from backtest.account_position import AccountPosition
from backtest.models import Direction
from backtest.netting import NettingResult
from backtest.target_position import TargetAccountPosition


def calculate_netting(
    current: AccountPosition | None,
    target: TargetAccountPosition | None,
) -> NettingResult:
    if current is None and target is None:
        raise ValueError(
            "current and target cannot both be flat"
        )

    if current is not None and target is None:
        return NettingResult(
            action="EXIT",
            direction=current.direction,
            quantity=current.quantity,
        )

    if current is None and target is not None:
        return NettingResult(
            action="ENTER",
            direction=target.direction,
            quantity=target.quantity,
        )

    if (
        current.symbol != target.symbol
        or current.contract != target.contract
        or current.direction != target.direction
    ):
        raise NotImplementedError(
            "position identity changes are not implemented"
        )

    if target.quantity > current.quantity:
        return NettingResult(
            action="ADD",
            direction=target.direction,
            quantity=target.quantity - current.quantity,
        )

    if target.quantity < current.quantity:
        return NettingResult(
            action="REDUCE",
            direction=target.direction,
            quantity=current.quantity - target.quantity,
        )

    return NettingResult(
        action="HOLD",
        direction=target.direction,
        quantity=target.quantity,
    )
