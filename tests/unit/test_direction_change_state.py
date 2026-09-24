from backtest.account_position import AccountPosition
from backtest.direction_change import DirectionChangeState
from backtest.direction_change_state import advance_direction_change_state
from backtest.models import Direction


def make_position() -> AccountPosition:
    return AccountPosition(
        symbol="TXF",
        contract="TX1",
        direction=Direction.LONG,
        quantity=1,
    )


def test_exit_required_waits_for_flat():
    assert (
        advance_direction_change_state(
            DirectionChangeState.EXIT_REQUIRED,
            make_position(),
        )
        == DirectionChangeState.WAITING_FOR_FLAT
    )


def test_exit_required_can_re_evaluate_when_already_flat():
    assert (
        advance_direction_change_state(
            DirectionChangeState.EXIT_REQUIRED,
            None,
        )
        == DirectionChangeState.RE_EVALUATE
    )


def test_waiting_for_flat_stays_waiting_until_flat():
    assert (
        advance_direction_change_state(
            DirectionChangeState.WAITING_FOR_FLAT,
            make_position(),
        )
        == DirectionChangeState.WAITING_FOR_FLAT
    )


def test_waiting_for_flat_reaches_re_evaluate_when_flat():
    assert (
        advance_direction_change_state(
            DirectionChangeState.WAITING_FOR_FLAT,
            None,
        )
        == DirectionChangeState.RE_EVALUATE
    )
