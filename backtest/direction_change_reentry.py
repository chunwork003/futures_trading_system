from __future__ import annotations

from backtest.direction_change import DirectionChangeState
from backtest.target_position import TargetAccountPosition


def determine_reentry_state(
    state: DirectionChangeState,
    target: TargetAccountPosition | None,
) -> DirectionChangeState:
    if state != DirectionChangeState.RE_EVALUATE:
        return state

    if target is None:
        return DirectionChangeState.RE_EVALUATE

    return DirectionChangeState.ENTER_NEW_DIRECTION
