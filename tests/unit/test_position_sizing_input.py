from backtest.position_sizing import PositionSizingInput


def test_position_sizing_input_accepts_required_values():
    sizing_input = PositionSizingInput(
        equity=1_000_000,
        price=20_000,
        stop_price=19_900,
        multiplier=200,
        risk_budget=0.01,
    )

    assert sizing_input.equity == 1_000_000
    assert sizing_input.price == 20_000
    assert sizing_input.stop_price == 19_900
    assert sizing_input.multiplier == 200
    assert sizing_input.risk_budget == 0.01
