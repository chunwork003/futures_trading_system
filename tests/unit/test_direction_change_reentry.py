from backtest.direction_change import DirectionChangeState
from backtest.direction_change_reentry import determine_reentry_state
from backtest.models import Direction
from backtest.target_position import TargetAccountPosition


def make_target() -> TargetAccountPosition:
    return TargetAccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.SHORT,
        quantity=1,
    )


def test_re_evaluate_waits_when_no_new_target():
    assert (
        determine_reentry_state(
            DirectionChangeState.RE_EVALUATE,
            None,
        )
        == DirectionChangeState.RE_EVALUATE
    )


def test_re_evaluate_enters_new_direction_with_new_target():
    assert (
        determine_reentry_state(
            DirectionChangeState.RE_EVALUATE,
            make_target(),
        )
        == DirectionChangeState.ENTER_NEW_DIRECTION
    )


def test_non_re_evaluate_state_is_unchanged():
    assert (
        determine_reentry_state(
            DirectionChangeState.WAITING_FOR_FLAT,
            make_target(),
        )
        == DirectionChangeState.WAITING_FOR_FLAT
    )
