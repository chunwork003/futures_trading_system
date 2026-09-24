from backtest.account_position import AccountPosition
from backtest.direction_change import DirectionChangeState
from backtest.direction_change_reentry import determine_reentry_state
from backtest.direction_change_state import advance_direction_change_state
from backtest.direction_change_transition import (
    determine_direction_change_state,
)
from backtest.models import Direction
from backtest.target_position import TargetAccountPosition


def make_current() -> AccountPosition:
    return AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=1,
    )


def make_short_target() -> TargetAccountPosition:
    return TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.SHORT,
        quantity=1,
    )


def test_long_to_short_requires_flat_before_reentry():
    current = make_current()
    target = make_short_target()

    state = determine_direction_change_state(
        current,
        target,
    )

    assert state == DirectionChangeState.EXIT_REQUIRED

    state = advance_direction_change_state(
        state,
        current,
    )

    assert state == DirectionChangeState.WAITING_FOR_FLAT

    state = advance_direction_change_state(
        state,
        None,
    )

    assert state == DirectionChangeState.RE_EVALUATE

    state = determine_reentry_state(
        state,
        target,
    )

    assert state == DirectionChangeState.ENTER_NEW_DIRECTION
