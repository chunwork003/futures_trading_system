from backtest.polling_result import PollingResult


def test_polling_result_stores_iterations_and_results():
    result = PollingResult(
        iterations=2,
        results=["first", "second"],
    )

    assert result.iterations == 2
    assert result.results == ["first", "second"]
