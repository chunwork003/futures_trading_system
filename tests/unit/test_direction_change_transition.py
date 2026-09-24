from backtest.account_position import AccountPosition
from backtest.direction_change import DirectionChangeState
from backtest.direction_change_transition import (
    determine_direction_change_state,
)
from backtest.models import Direction
from backtest.target_position import TargetAccountPosition


def make_current(direction: Direction) -> AccountPosition:
    return AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=direction,
        quantity=1,
    )


def make_target(direction: Direction) -> TargetAccountPosition:
    return TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=direction,
        quantity=1,
    )


def test_same_direction_has_no_change():
    assert (
        determine_direction_change_state(
            make_current(Direction.LONG),
            make_target(Direction.LONG),
        )
        == DirectionChangeState.NO_CHANGE
    )


def test_long_to_short_requires_exit():
    assert (
        determine_direction_change_state(
            make_current(Direction.LONG),
            make_target(Direction.SHORT),
        )
        == DirectionChangeState.EXIT_REQUIRED
    )


def test_short_to_long_requires_exit():
    assert (
        determine_direction_change_state(
            make_current(Direction.SHORT),
            make_target(Direction.LONG),
        )
        == DirectionChangeState.EXIT_REQUIRED
    )


def test_current_position_with_flat_target_requires_exit():
    assert (
        determine_direction_change_state(
            make_current(Direction.LONG),
            None,
        )
        == DirectionChangeState.EXIT_REQUIRED
    )


def test_flat_account_with_target_enters_new_direction():
    assert (
        determine_direction_change_state(
            None,
            make_target(Direction.SHORT),
        )
        == DirectionChangeState.ENTER_NEW_DIRECTION
    )


def test_both_flat_has_no_change():
    assert (
        determine_direction_change_state(
            None,
            None,
        )
        == DirectionChangeState.NO_CHANGE
    )
