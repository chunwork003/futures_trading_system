from __future__ import annotations

import json

import pytest

from backtest.monte_carlo import (
    MonteCarloConfig,
    MonteCarloEngine,
    MonteCarloMode,
    run_monte_carlo,
)


def test_empty_trade_pnls_rejected() -> None:
    engine = MonteCarloEngine(MonteCarloConfig())

    with pytest.raises(ValueError, match="trade_pnls must not be empty"):
        engine.run([])


def test_invalid_config_rejected() -> None:
    with pytest.raises(ValueError, match="simulations must be greater than 0"):
        MonteCarloConfig(simulations=0)

    with pytest.raises(ValueError, match="initial_capital must be greater than 0"):
        MonteCarloConfig(initial_capital=0)


def test_shuffle_preserves_total_pnl() -> None:
    trade_pnls = [100.0, -200.0, 50.0]

    engine = MonteCarloEngine(
        MonteCarloConfig(
            simulations=10,
            initial_capital=1_000.0,
            seed=42,
        )
    )

    report = engine.run(
        trade_pnls,
        mode=MonteCarloMode.SHUFFLE,
    )

    assert report.trade_count == 3
    assert report.original_total_pnl == pytest.approx(-50.0)

    for result in report.simulations_result:
        assert result.total_pnl == pytest.approx(-50.0)
        assert result.final_equity == pytest.approx(950.0)


def test_shuffle_seed_is_deterministic() -> None:
    trade_pnls = [100.0, -200.0, 50.0]

    config = MonteCarloConfig(
        simulations=20,
        initial_capital=1_000.0,
        seed=42,
    )

    report_a = MonteCarloEngine(config).run(
        trade_pnls,
        mode=MonteCarloMode.SHUFFLE,
    )

    report_b = MonteCarloEngine(config).run(
        trade_pnls,
        mode=MonteCarloMode.SHUFFLE,
    )

    assert report_a.to_dict() == report_b.to_dict()


def test_bootstrap_is_deterministic() -> None:
    trade_pnls = [100.0, -200.0, 50.0]

    config = MonteCarloConfig(
        simulations=20,
        initial_capital=1_000.0,
        seed=42,
    )

    report_a = MonteCarloEngine(config).run(
        trade_pnls,
        mode=MonteCarloMode.BOOTSTRAP,
    )

    report_b = MonteCarloEngine(config).run(
        trade_pnls,
        mode=MonteCarloMode.BOOTSTRAP,
    )

    assert report_a.to_dict() == report_b.to_dict()


def test_bootstrap_can_change_total_pnl() -> None:
    trade_pnls = [100.0, -200.0, 50.0]

    engine = MonteCarloEngine(
        MonteCarloConfig(
            simulations=100,
            initial_capital=1_000.0,
            seed=42,
        )
    )

    report = engine.run(
        trade_pnls,
        mode=MonteCarloMode.BOOTSTRAP,
    )

    totals = {
        round(result.total_pnl, 8)
        for result in report.simulations_result
    }

    assert len(totals) > 1


def test_drawdown_first_loss_is_peak_relative() -> None:
    engine = MonteCarloEngine(
        MonteCarloConfig(
            simulations=1,
            initial_capital=1_000.0,
            seed=42,
        )
    )

    result = engine._simulate([-200.0])

    assert result.final_equity == pytest.approx(800.0)
    assert result.total_pnl == pytest.approx(-200.0)
    assert result.max_drawdown == pytest.approx(-200.0)
    assert result.max_drawdown_pct == pytest.approx(-0.20)


def test_drawdown_after_new_peak_is_peak_relative() -> None:
    engine = MonteCarloEngine(
        MonteCarloConfig(
            simulations=1,
            initial_capital=1_000.0,
            seed=42,
        )
    )

    result = engine._simulate([100.0, -200.0])

    assert result.final_equity == pytest.approx(900.0)
    assert result.total_pnl == pytest.approx(-100.0)
    assert result.max_drawdown == pytest.approx(-200.0)
    assert result.max_drawdown_pct == pytest.approx(-200.0 / 1100.0)


def test_run_monte_carlo_wrapper_accepts_simulations() -> None:
    report = run_monte_carlo(
        [100.0, -200.0, 50.0],
        simulations=7,
        initial_capital=1_000.0,
        seed=42,
        mode=MonteCarloMode.SHUFFLE,
    )

    assert report.simulations == 7
    assert report.trade_count == 3
    assert len(report.simulations_result) == 7
    assert report.initial_capital == pytest.approx(1_000.0)


def test_report_percentiles_are_ordered() -> None:
    engine = MonteCarloEngine(
        MonteCarloConfig(
            simulations=100,
            initial_capital=1_000.0,
            seed=42,
        )
    )

    report = engine.run(
        [100.0, -200.0, 50.0],
        mode=MonteCarloMode.BOOTSTRAP,
    )

    assert report.p05_final_equity <= report.median_final_equity
    assert report.median_final_equity <= report.p95_final_equity

    assert report.p05_total_pnl <= report.median_total_pnl
    assert report.median_total_pnl <= report.p95_total_pnl

    assert report.p05_max_drawdown <= report.median_max_drawdown
    assert report.median_max_drawdown <= report.p95_max_drawdown

    assert report.p05_max_drawdown_pct <= report.median_max_drawdown_pct
    assert report.median_max_drawdown_pct <= report.p95_max_drawdown_pct


def test_report_to_dict_is_json_serializable() -> None:
    engine = MonteCarloEngine(
        MonteCarloConfig(
            simulations=10,
            initial_capital=1_000.0,
            seed=42,
        )
    )

    report = engine.run(
        [100.0, -200.0, 50.0],
        mode=MonteCarloMode.SHUFFLE,
    )

    payload = report.to_dict()

    assert payload["mode"] == "SHUFFLE"
    assert payload["trade_count"] == 3
    assert payload["simulations"] == 10

    json.dumps(payload)
