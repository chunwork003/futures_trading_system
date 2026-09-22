from backtest.polling import PollingConfig
from backtest.polling_loop import PollingLoop


def test_polling_loop_runs_callback_requested_times():
    calls = []

    loop = PollingLoop(
        callback=lambda: calls.append(1),
        config=PollingConfig(interval_seconds=0.001),
    )

    result = loop.run(max_iterations=3)

    assert len(calls) == 3
    assert result.iterations == 3


def test_polling_loop_collects_callback_results():
    loop = PollingLoop(
        callback=lambda: "processed",
        config=PollingConfig(interval_seconds=0.001),
    )

    result = loop.run(max_iterations=2)

    assert result.iterations == 2
    assert result.results == ["processed", "processed"]
