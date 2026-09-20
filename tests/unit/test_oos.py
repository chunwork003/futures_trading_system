from datetime import datetime

import pytest

from backtest.oos import OOSAggregator, aggregate_oos_results
from backtest.walk_forward_optimization import (
    WalkForwardOptimizationResult,
)


def make_result(
    window_id: int,
    parameter_id: str,
    net_profit: float,
    expectancy: float,
    profit_factor: float,
    drawdown: float,
    trades: int = 100,
) -> WalkForwardOptimizationResult:
    return WalkForwardOptimizationResult(
        window_id=window_id,
        train_start=datetime(2026, 1, 1),
        train_end=datetime(2026, 2, 1),
        test_start=datetime(2026, 2, 2 + window_id),
        test_end=datetime(2026, 2, 3 + window_id),
        selected_parameter_id=parameter_id,
        selected_fast_window=20,
        selected_slow_window=60,
        train_trades=100,
        train_expectancy=100.0,
        train_profit_factor=1.05,
        train_max_drawdown_pct=-20.0,
        train_net_profit=10_000.0,
        oos_trades=trades,
        oos_expectancy=expectancy,
        oos_profit_factor=profit_factor,
        oos_max_drawdown_pct=drawdown,
        oos_net_profit=net_profit,
        oos_final_equity=1_000_000.0 + net_profit,
    )


def test_aggregate_empty_results_rejected():
    with pytest.raises(ValueError, match="results must not be empty"):
        OOSAggregator().aggregate([])


def test_aggregate_total_trade_and_pnl():
    results = [
        make_result(1, "ema_10_30", 1000.0, 10.0, 1.10, -5.0),
        make_result(2, "ema_20_60", 2000.0, 20.0, 1.20, -8.0),
        make_result(3, "ema_10_30", -500.0, -5.0, 0.90, -12.0),
    ]

    report = aggregate_oos_results(results)

    assert report.window_count == 3
    assert report.total_trades == 300
    assert report.total_net_profit == 2500.0


def test_positive_and_negative_window_count():
    results = [
        make_result(1, "ema_10_30", 1000.0, 10.0, 1.10, -5.0),
        make_result(2, "ema_20_60", -200.0, -2.0, 0.95, -9.0),
        make_result(3, "ema_10_30", 0.0, 0.0, 1.00, -7.0),
    ]

    report = aggregate_oos_results(results)

    assert report.positive_windows == 1
    assert report.negative_windows == 1
    assert report.non_negative_window_ratio == pytest.approx(2 / 3)
    assert report.oos_consistency_ratio == pytest.approx(1 / 3)


def test_parameter_frequency():
    results = [
        make_result(1, "ema_10_30", 1000.0, 10.0, 1.10, -5.0),
        make_result(2, "ema_20_60", 2000.0, 20.0, 1.20, -8.0),
        make_result(3, "ema_10_30", -500.0, -5.0, 0.90, -12.0),
    ]

    report = aggregate_oos_results(results)

    assert report.selected_parameter_count == 2
    assert report.parameter_frequencies[0].parameter_id == "ema_10_30"
    assert report.parameter_frequencies[0].selected_windows == 2
    assert report.parameter_frequencies[1].parameter_id == "ema_20_60"
    assert report.parameter_frequencies[1].selected_windows == 1


def test_best_worst_and_average_metrics():
    results = [
        make_result(1, "ema_10_30", 1000.0, 10.0, 1.10, -5.0),
        make_result(2, "ema_20_60", 2000.0, 20.0, 1.20, -8.0),
        make_result(3, "ema_10_30", -500.0, -5.0, 0.90, -12.0),
    ]

    report = aggregate_oos_results(results)

    assert report.best_window_net_profit == 2000.0
    assert report.worst_window_net_profit == -500.0
    assert report.worst_window_drawdown_pct == -12.0
    assert report.average_window_expectancy == pytest.approx(25 / 3)
    assert report.median_window_expectancy == 10.0


def test_to_dict_is_json_serializable():
    import json

    results = [
        make_result(1, "ema_10_30", 1000.0, 10.0, 1.10, -5.0),
    ]

    report = aggregate_oos_results(results)

    payload = report.to_dict()

    encoded = json.dumps(payload)

    assert isinstance(encoded, str)
    assert payload["window_count"] == 1
    assert payload["windows"][0]["parameter_id"] == "ema_10_30"
