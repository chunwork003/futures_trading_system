from __future__ import annotations

from backtest.account_position import AccountPosition
from backtest.direction_change import DirectionChangeState


def advance_direction_change_state(
    state: DirectionChangeState,
    account_position: AccountPosition | None,
) -> DirectionChangeState:
    if state == DirectionChangeState.EXIT_REQUIRED:
        if account_position is None:
            return DirectionChangeState.RE_EVALUATE

        return DirectionChangeState.WAITING_FOR_FLAT

    if state == DirectionChangeState.WAITING_FOR_FLAT:
        if account_position is None:
            return DirectionChangeState.RE_EVALUATE

        return DirectionChangeState.WAITING_FOR_FLAT

    return state
