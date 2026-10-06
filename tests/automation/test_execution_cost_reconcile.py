from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[2]
RECONCILER = ROOT / "scripts/execution_cost_reconcile.ps1"


def _powershell() -> str:
    executable = shutil.which("pwsh") or shutil.which("powershell")
    assert executable, "PowerShell is required for deterministic reconciliation verification"
    return executable


def _run(tmp_path: Path, forecast: dict, actual: dict) -> dict:
    forecast_path = tmp_path / "forecast.json"
    actual_path = tmp_path / "actual.json"
    forecast_path.write_text(json.dumps(forecast), encoding="utf-8")
    actual_path.write_text(json.dumps(actual), encoding="utf-8")
    output = subprocess.check_output(
        [
            _powershell(),
            "-NoProfile",
            "-File",
            str(RECONCILER),
            "-ForecastPath",
            str(forecast_path),
            "-ActualPath",
            str(actual_path),
        ],
        encoding="utf-8-sig",
    )
    return json.loads(output)


@pytest.fixture(params=["powershell", "pwsh"], autouse=True)
def compatibility_shell(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> str:
    # 每個 subprocess case 都經兩種解碼路徑；PS7 不存在時明確 SKIP。
    executable = shutil.which(request.param)
    if request.param == "powershell":
        assert executable, "Windows PowerShell 5.1 is REQUIRED"
    elif not executable:
        pytest.skip("PowerShell 7 NOT_AVAILABLE")
    assert executable
    monkeypatch.setattr(__import__(__name__, fromlist=["_powershell"]), "_powershell", lambda: executable)
    return executable


def test_shell_version_and_utf8_bom(compatibility_shell: str) -> None:
    version = subprocess.check_output(
        [compatibility_shell, "-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"],
        encoding="utf-8-sig",
    ).strip()
    if Path(compatibility_shell).name.lower().startswith("powershell"):
        assert version.startswith("5.1.")
    else:
        assert version.startswith("7.")
    assert RECONCILER.read_bytes().startswith(b"\xef\xbb\xbf")


def _forecast() -> dict:
    return {
        "schema_version": "automation.execution_cost_forecast.v1",
        "confidence": "PROVISIONAL",
        "forecast": {
            "reported_total_tokens": {"p50": 100, "p75": 150, "p90": 200},
            "uncached_input_tokens": {"p50": 40, "p75": 60, "p90": 80},
            "five_hour_delta_pct": {"p50": 1, "p75": 2, "p90": 3},
            "actor_seconds": {"p50": 10, "p75": 20, "p90": 30},
        },
    }


def _actual(**updates: object) -> dict:
    actual = {
        "reported_total_tokens": 100,
        "uncached_input_tokens": 40,
        "cached_input_ratio": 0.50,
        "five_hour_delta_pct": 1,
        "actor_seconds": 10,
    }
    actual.update(updates)
    return {
        "schema_version": "automation.execution_cost_actual.v1",
        "work_order_id": "WO",
        "execution_id": "EXEC",
        "actual": actual,
    }


def test_fresh_context_growth_never_auto_splits(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        _forecast(),
        _actual(
            reported_total_tokens=250,
            uncached_input_tokens=120,
            cached_input_ratio=0.20,
        ),
    )
    assert result["dominant_cause"] == "FRESH_CONTEXT_GROWTH"
    assert "TIGHTEN_POINTER_FIRST_CONTEXT" in result["recommendations"]
    assert "REMOVE_UNRELATED_HISTORY" in result["recommendations"]
    assert "RECALIBRATE_UNCACHED_INPUT_FORECAST" in result["recommendations"]
    assert "SPLIT_OVERSIZED_WORK_ORDER" not in result["recommendations"]
    assert result["work_package_sizing_assessment"] == "NO_AUTOMATIC_SPLIT"
    assert result["split_authority_created"] is False


def test_structural_split_evidence_is_non_authority_assessment_only(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        _forecast(),
        _actual(
            structural_sizing_evidence={
                "genuinely_oversized_work_package": True,
                "positive_total_lifecycle_roi": True,
            }
        ),
    )
    assert result["work_package_sizing_assessment"] == "STRUCTURAL_SPLIT_CANDIDATE_NON_AUTHORITY"
    assert "WORK_REVIEW_STRUCTURAL_SPLIT_CANDIDATE" in result["recommendations"]
    assert result["split_authority_created"] is False


def test_provider_pause_metrics_remain_backward_compatible(tmp_path: Path) -> None:
    result = _run(
        tmp_path,
        _forecast(),
        _actual(
            provider_limit_encountered=True,
            provider_pause_count=1,
            provider_pause_seconds=30,
            resume_count=1,
            resumed_same_execution=True,
        ),
    )
    assert result["forecast_capacity_review_required"] is True
    assert result["provider_pause_is_source_defect"] is False
    assert result["provider_interruption"]["provider_pause_count"] == 1
    assert "WORK_FORECAST_CAPACITY_REVIEW_PRESERVE_SAME_EXECUTION" in result["recommendations"]


def test_current_procedure_documents_no_longer_claim_capacity_source_pending() -> None:
    paths = (
        ROOT / "automation/skills/repo-reentry/SKILL.md",
        ROOT / "automation/skills/single-use-lifecycle-guard/SKILL.md",
        ROOT / "automation/skills/execution-cost-forecaster/SKILL.md",
        ROOT / "automation/prompts/WORK_ORCHESTRATOR_KERNEL.md",
        ROOT / "automation/prompts/CODEX_EXECUTOR_KERNEL.md",
    )
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "Main evaluator/tests source update pending in same21files" not in text
        assert "HUMAN_DIALOGUE is a permanent supported MANUAL executor fallback" in text
        assert "same execution multi-executor is DENIED" in text


def test_context_policy_points_to_active_v2_accounting_and_manual_fallback() -> None:
    text = (ROOT / "automation/specs/context_loading_policy.v1.yaml").read_text(encoding="utf-8")
    assert "pointer: automation/specs/work_cost_accounting.v2.yaml" in text
    assert "version: '1.2.2'" in text
    assert "human_dialogue_codex_capacity_gate: NOT_APPLICABLE" in text
    assert "proxy_content_estimate_is_exact_usage: false" in text



def test_missing_optional_forecast_and_actual_metrics_are_null_safe(
    tmp_path: Path,
) -> None:
    forecast = {
        "schema_version": "automation.execution_cost_forecast.v1",
        "confidence": "PROVISIONAL",
        "forecast": {
            "actor_seconds": {"p50": 10, "p75": 20, "p90": 30},
        },
    }
    actual = {
        "schema_version": "automation.execution_cost_actual.v1",
        "work_order_id": "WO",
        "execution_id": "EXEC",
        "actual": {
            "actor_seconds": 10,
            "provider_limit_encountered": True,
            "provider_pause_count": 1,
            "provider_pause_seconds": 30,
            "resume_count": 1,
            "resumed_same_execution": True,
        },
    }

    result = _run(tmp_path, forecast, actual)

    assert result["overall_classification"] == "NORMAL"
    assert result["dominant_cause"] == "WITHIN_EXPECTED_ENVELOPE"
    assert result["forecast_capacity_review_required"] is True
    assert result["provider_pause_is_source_defect"] is False
    assert result["split_authority_created"] is False



def test_minimal_legacy_payload_omits_all_optional_diagnostic_fields(
    tmp_path: Path,
) -> None:
    forecast = {
        "schema_version": "automation.execution_cost_forecast.v1",
        "confidence": "PROVISIONAL",
        "forecast": {},
    }
    actual = {
        "schema_version": "automation.execution_cost_actual.v1",
        "work_order_id": "WO-LEGACY",
        "execution_id": "EXEC-LEGACY",
        "actual": {},
    }

    result = _run(tmp_path, forecast, actual)

    assert result["overall_classification"] == "NORMAL"
    assert result["dominant_cause"] == "WITHIN_EXPECTED_ENVELOPE"
    assert result["metric_comparisons"] == []
    assert result["cycle_breaches"] == []
    assert result["forecast_capacity_review_required"] is False
    assert result["provider_interruption"] == {}
    assert result["work_package_sizing_assessment"] == "NO_AUTOMATIC_SPLIT"
    assert result["split_authority_created"] is False


def test_partial_optional_nested_forecast_bands_are_null_safe(
    tmp_path: Path,
) -> None:
    forecast = {
        "schema_version": "automation.execution_cost_forecast.v1",
        "confidence": "PROVISIONAL",
        "forecast": {
            "reported_total_tokens": {"p50": 100, "p75": 150, "p90": 200},
        },
    }
    actual = {
        "schema_version": "automation.execution_cost_actual.v1",
        "work_order_id": "WO-PARTIAL",
        "execution_id": "EXEC-PARTIAL",
        "actual": {
            "reported_total_tokens": 100,
        },
    }

    result = _run(tmp_path, forecast, actual)

    assert result["overall_classification"] == "NORMAL"
    assert result["dominant_cause"] == "WITHIN_EXPECTED_ENVELOPE"
    assert result["forecast_capacity_review_required"] is False
    assert result["split_authority_created"] is False


@pytest.mark.parametrize("family", ["bands", "test_cycles", "structural_evidence"])
@pytest.mark.parametrize("shape", ["absent", "null", "partial"])
def test_optional_nested_shapes_preserve_legacy_semantics(
    tmp_path: Path, family: str, shape: str,
) -> None:
    forecast = {"schema_version": "automation.execution_cost_forecast.v1",
                "confidence": "PROVISIONAL", "forecast": {}}
    actual = {"schema_version": "automation.execution_cost_actual.v1",
              "work_order_id": "WO", "execution_id": "EXEC", "actual": {}}
    if family == "bands":
        if shape != "absent":
            forecast["forecast"]["reported_total_tokens"] = None if shape == "null" else {"p90": 200}
            actual["actual"]["reported_total_tokens"] = None if shape == "null" else 100
    elif family == "test_cycles":
        if shape != "absent":
            forecast["forecast"]["test_cycles"] = None if shape == "null" else {"pre_fix_cases_max": 1}
            actual["actual"]["test_cycles"] = None if shape == "null" else {"pre_fix_cases": 0}
    elif shape != "absent":
        actual["actual"]["structural_sizing_evidence"] = (
            None if shape == "null" else {"genuinely_oversized_work_package": True}
        )
    result = _run(tmp_path, forecast, actual)
    assert result["overall_classification"] == "NORMAL"
    assert result["dominant_cause"] == "WITHIN_EXPECTED_ENVELOPE"
    assert result["metric_comparisons"] == []
    assert result["cycle_breaches"] == []
    assert result["provider_interruption"] == {}
    assert result["forecast_capacity_review_required"] is False
    assert result["provider_pause_is_source_defect"] is False
    assert result["split_authority_created"] is False
    expected_sizing = ("STRUCTURAL_SPLIT_NOT_ESTABLISHED"
                       if family == "structural_evidence" and shape == "partial"
                       else "NO_AUTOMATIC_SPLIT")
    assert result["work_package_sizing_assessment"] == expected_sizing
    assert "WORK_REVIEW_STRUCTURAL_SPLIT_CANDIDATE" not in result["recommendations"]


def test_pause_false_positive_control_preserves_telemetry(tmp_path: Path) -> None:
    result = _run(tmp_path, _forecast(), _actual(
        provider_limit_encountered=False, provider_pause_count=0,
        provider_pause_seconds=0, resume_count=0, resumed_same_execution=False,
    ))
    assert result["provider_interruption"] == {
        "provider_limit_encountered": False, "provider_pause_count": 0,
        "provider_pause_seconds": 0, "resume_count": 0, "resumed_same_execution": False,
    }
    assert result["forecast_capacity_review_required"] is False
    assert result["provider_pause_is_source_defect"] is False
    assert result["split_authority_created"] is False
