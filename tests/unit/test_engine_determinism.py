def test_changing_input_data_changes_backtest_result():
    bars, signals = make_test_data()

    engine_original = BacktestEngine(make_config())
    original_trades = engine_original.run(
        bars,
        signals,
    )

    modified_bars = list(bars)

    # EXIT signal is generated on T+1
    # and executed at T+2 OPEN.
    modified_bars[2] = make_bar(
        BASE_TIME + timedelta(minutes=2),
        25_015,
        25_020,
        25_005,
        25_015,
    )

    engine_modified = BacktestEngine(make_config())
    modified_trades = engine_modified.run(
        modified_bars,
        signals,
    )

    assert len(original_trades) == 1
    assert len(modified_trades) == 1

    original_trade = original_trades[0]
    modified_trade = modified_trades[0]

    # Regression:
    # EXIT signal generated on T+1
    # must execute at T+2 OPEN.
    #
    # Original:
    # OPEN = 25,010
    # Long exit slippage = 1
    # Actual exit fill = 25,009
    assert original_trade.exit_price == 25_009

    # Modified:
    # OPEN = 25,015
    # Long exit slippage = 1
    # Actual exit fill = 25,014
    assert modified_trade.exit_price == 25_014

    assert (
        original_trade.model_dump()
        != modified_trade.model_dump()
    )

    assert (
        engine_original.portfolio.realized_pnl
        != engine_modified.portfolio.realized_pnl
    )