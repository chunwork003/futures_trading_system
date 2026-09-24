from backtest.direction_change import DirectionChangeState


def test_direction_change_states():
    assert DirectionChangeState.NO_CHANGE.value == "NO_CHANGE"
    assert DirectionChangeState.EXIT_REQUIRED.value == "EXIT_REQUIRED"
    assert DirectionChangeState.WAITING_FOR_FLAT.value == "WAITING_FOR_FLAT"
    assert DirectionChangeState.RE_EVALUATE.value == "RE_EVALUATE"
    assert (
        DirectionChangeState.ENTER_NEW_DIRECTION.value
        == "ENTER_NEW_DIRECTION"
    )
