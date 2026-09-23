from __future__ import annotations

from backtest.account_position import AccountPosition
from backtest.decision import DecisionAction
from backtest.target_position import TargetAccountPosition


def determine_decision_action(
    current: AccountPosition | None,
    target: TargetAccountPosition | None,
) -> DecisionAction:
    if current is None and target is None:
        raise ValueError("current and target cannot both be flat")

    if target is None:
        return DecisionAction.EXIT

    if current is None:
        return DecisionAction.ENTER

    same_position = (
        current.symbol == target.symbol
        and current.contract == target.contract
        and current.direction == target.direction
    )

    if same_position and current.quantity == target.quantity:
        return DecisionAction.HOLD

    if same_position and target.quantity > current.quantity:
        return DecisionAction.ADD

    if same_position and target.quantity < current.quantity:
        return DecisionAction.REDUCE

    raise NotImplementedError(
        "decision action is not implemented for this position transition"
    )
