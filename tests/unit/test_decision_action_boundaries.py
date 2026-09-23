import pytest

from backtest.decision_action import determine_decision_action


def test_determine_decision_action_rejects_both_positions_flat():
    with pytest.raises(ValueError, match="both be flat"):
        determine_decision_action(
            None,
            None,
        )
