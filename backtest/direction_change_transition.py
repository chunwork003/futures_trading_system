from __future__ import annotations

from backtest.account_position import AccountPosition
from backtest.direction_change import DirectionChangeState
from backtest.target_position import TargetAccountPosition


def determine_direction_change_state(
    current: AccountPosition | None,
    target: TargetAccountPosition | None,
) -> DirectionChangeState:
    if current is None:
        if target is None:
            return DirectionChangeState.NO_CHANGE

        return DirectionChangeState.ENTER_NEW_DIRECTION

    if target is None:
        return DirectionChangeState.EXIT_REQUIRED

    same_position = (
        current.symbol == target.symbol
        and current.contract == target.contract
        and current.direction == target.direction
    )

    if same_position:
        return DirectionChangeState.NO_CHANGE

    return DirectionChangeState.EXIT_REQUIRED
