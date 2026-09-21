from __future__ import annotations

from scripts.analyze_monte_carlo import _load_reports
from analysis.monte_carlo_report import analyze_monte_carlo_report


def _report(mode: str) -> dict:
    return {
        "mode": mode,
        "trade_count": 2,
        "simulations": 2,
        "initial_capital": 1_000_000.0,
        "original_total_pnl": -100.0,
        "original_final_equity": 999_900.0,
        "simulations_result": [
            {
                "final_equity": 999_900.0,
                "total_pnl": -100.0,
                "max_drawdown": -200.0,
                "max_drawdown_pct": -0.0002,
            },
            {
                "final_equity": 999_900.0,
                "total_pnl": -100.0,
                "max_drawdown": -300.0,
                "max_drawdown_pct": -0.0003,
            },
        ],
    }


def test_nested_monte_carlo_report_loads_shuffle_and_bootstrap() -> None:
    payload = {
        "shuffle": _report("SHUFFLE"),
        "bootstrap": _report("BOOTSTRAP"),
    }

    import json
    from pathlib import Path
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "monte_carlo.json"

        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle)

        reports = _load_reports(path)

    assert set(reports) == {"shuffle", "bootstrap"}
    assert reports["shuffle"]["mode"] == "SHUFFLE"
    assert reports["bootstrap"]["mode"] == "BOOTSTRAP"


def test_nested_reports_are_independently_analyzable() -> None:
    payload = {
        "shuffle": _report("SHUFFLE"),
        "bootstrap": _report("BOOTSTRAP"),
    }

    reports = {
        mode: analyze_monte_carlo_report(report)
        for mode, report in payload.items()
    }

    assert reports["shuffle"].mode == "SHUFFLE"
    assert reports["bootstrap"].mode == "BOOTSTRAP"
    assert reports["shuffle"].original_total_pnl == -100.0
    assert reports["bootstrap"].original_final_equity == 999_900.0
