from __future__ import annotations

import pytest

from backtest.monte_carlo import (
    MonteCarloConfig,
    MonteCarloEngine,
    MonteCarloMode,
    run_monte_carlo,
)


def test_empty_trade_pnls_rejected() -> None:
    engine = MonteCarloEngine(MonteCarloConfig())

    with pytest.raises(ValueError, match="must not be empty"):
        engine.run([])


def test_invalid_config_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="simulations must be greater than 0",
    ):
        MonteCarloConfig(simulations=0)

    with pytest.raises(
        ValueError,
        match="initial_capital must be greater than 0",
    ):
        MonteCarloConfig(initial_capital=0)


def test_shuffle_preserves_total_pnl() -> None:
    pnls = [100.0, -50.0, 200.0, -25.0]

    report = run_monte_carlo(
        pnls,
        simulations=100,
        seed=42,
        mode=MonteCarloMode.SHUFFLE,
    )

    assert report.trade_count == 4
    assert report.original_total_pnl == 225.0
    assert report.original_final_equity == 1_000_225.0

    assert all(
        result.total_pnl == 225.0
        for result in report.simulations_result
    )


def test_shuffle_seed_is_deterministic() -> None:
    pnls = [100.0, -50.0, 200.0, -25.0]

    first = run_monte_carlo(
        pnls,
        simulations=100,
        seed=42,
        mode=MonteCarloMode.SHUFFLE,
    )

    second = run_monte_carlo(
        pnls,
        simulations=100,
        seed=42,
        mode=MonteCarloMode.SHUFFLE,
    )

    assert first == second


def test_bootstrap_is_deterministic() -> None:
    pnls = [100.0, -50.0, 200.0, -25.0]

    first = run_monte_carlo(
        pnls,
        simulations=100,
        seed=42,
        mode=MonteCarloMode.BOOTSTRAP,
    )

    second = run_monte_carlo(
        pnls,
        simulations=100,
        seed=42,
        mode=MonteCarloMode.BOOTSTRAP,
    )

    assert first == second


def test_bootstrap_can_change_total_pnl() -> None:
    pnls = [100.0, -50.0, 200.0, -25.0]

    report = run_monte_carlo(
        pnls,
        simulations=100,
        seed=42,
        mode=MonteCarloMode.BOOTSTRAP,
    )

    totals = {
        result.total_pnl
        for result in report.simulations_result
    }

    assert len(totals) > 1


def test_drawdown_calculation() -> None:
    pnls = [100.0, -200.0, 50.0]

    report = run_monte_carlo(
        pnls,
        simulations=1,
        initial_capital=1_000.0,
        seed=42,
        mode=MonteCarloMode.SHUFFLE,
    )

    result = report.simulations_result[0]

    assert result.final_equity == 950.0
    assert result.total_pnl == -50.0
    assert result.max_drawdown == -200.0
    assert result.max_drawdown_pct == pytest.approx(-0.20)


def test_report_percentiles_are_ordered() -> None:
    pnls = [100.0, -50.0, 200.0, -25.0]

    report = run_monte_carlo(
        pnls,
        simulations=1000,
        seed=42,
        mode=MonteCarloMode.BOOTSTRAP,
    )

    assert report.p05_total_pnl <= report.median_total_pnl
    assert report.median_total_pnl <= report.p95_total_pnl

    assert (
        report.p05_final_equity
        <= report.median_final_equity
        <= report.p95_final_equity
    )


def test_to_dict_is_json_serializable() -> None:
    import json

    report = run_monte_carlo(
        [100.0, -50.0, 200.0],
        simulations=10,
        seed=42,
    )

    payload = report.to_dict()

    json.dumps(payload)

    assert payload["mode"] == "SHUFFLE"
    assert payload["trade_count"] == 3
    assert payload["simulations"] == 10
