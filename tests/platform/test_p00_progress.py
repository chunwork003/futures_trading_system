"""候選進度分母與負向證據測試；不替產品完成度背書。"""

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("p00_progress", ROOT / "scripts/p00_progress.py")
progress = importlib.util.module_from_spec(spec)
spec.loader.exec_module(progress)


def baseline():
    return json.loads((ROOT / "docs/program/program_baseline.v1.json").read_text(encoding="utf-8"))


def test_current_report_does_not_claim_zero_product_or_eta():
    result = progress.calculate(baseline())
    assert result["total_v1_packages_remaining"] == 13
    assert result["critical_packages_remaining"] == 9
    assert result["engineering_effort_days_excluding_p00"] == [71, 111]
    assert result["product_completion"].startswith("UNCALIBRATED")
    assert result["v1_engineering_weight_completion"].startswith("UNCALIBRATED")
    assert result["eta"] == dict.fromkeys(("optimistic", "base", "conservative"))
    assert result["weight_by_package"]["P00"] == 0
    assert result["execution_eligible"] is False


@pytest.mark.parametrize("pid", ["P01", "P02"])
def test_exact_candidate_deliverable_weights_preserved(pid):
    candidate = json.loads((ROOT / f"docs/program/packages/{pid}.candidate.v1.json").read_text(encoding="utf-8"))
    weights = {r["id"]: r["weight"] for r in baseline()["deliverables"] if r["package"] == pid}
    assert weights == candidate["identity"]["deliverable_weights"]


def test_split_and_correction_conserve_progress():
    old = baseline()
    new = copy.deepcopy(old)
    first = new["deliverables"][0]
    first["allocations"] = [{"id": "import-parse", "weight": 1}, {"id": "import-publish", "weight": 3}]
    new["corrections"] = [{"id": "RF-fixture", "deliverable": first["id"], "added_weight": 0}]
    progress.validate_regrouping(old, new)
    assert progress.calculate(old) == progress.calculate(new)


@pytest.mark.parametrize("mutation", [
    lambda b: b["packages"][0]["dependencies"].append("P12"),
    lambda b: b["packages"][1]["dependencies"].append("UNKNOWN"),
    lambda b: b["deliverables"].append(copy.deepcopy(b["deliverables"][0])),
    lambda b: b["deliverables"][0].update(weight=True),
    lambda b: b["deliverables"][0]["allocations"][0].update(weight=5),
    lambda b: b["deliverables"][0].update(package="P00"),
    lambda b: b["deliverables"][0]["gates"].update(implementation={"claim": "PASS"}),
    lambda b: b["packages"][1].update(acceptance={"claim": "PASS"}),
    lambda b: b["journeys"][0].update(evidence={"claim": "PASS"}),
    lambda b: b["corrections"].append({"id": "RF1", "deliverable": "P01-IMPORT", "added_weight": 1}),
    lambda b: b["eta"].update(base="next week"),
    lambda b: b.update(critical_chain_hypothesis=["P00", "P08"]),
    lambda b: b["packages"][1].update(effort_days=[9, 6]),
])
def test_reject_unsafe_or_inconsistent_accounting(mutation):
    value = baseline()
    mutation(value)
    with pytest.raises(ValueError):
        progress.calculate(value)


def test_same_revision_cannot_silently_reweight_even_when_internal_sum_matches():
    old = baseline()
    new = copy.deepcopy(old)
    new["deliverables"][0]["weight"] = 5
    new["deliverables"][0]["allocations"][0]["weight"] = 5
    with pytest.raises(ValueError, match="baseline revision"):
        progress.validate_regrouping(old, new)
