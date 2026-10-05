from __future__ import annotations

from pathlib import Path
from types import MappingProxyType

import pytest
from pydantic import ValidationError

from automation.engine.contracts import (
    AuthorizationLifecyclePolicy,
    AuthorizationRecord,
    DevelopmentEntryProtocol,
    DevelopmentStateMachinePolicy,
    ImplementationProgram,
    MasterManifest,
    QuotaAdmissionPolicy,
    WorkPackageRecord,
)
from automation.engine.yaml_io import (
    AutomationYamlError,
    load_yaml_contract,
    load_yaml_mapping,
)


ROOT = Path(__file__).resolve().parents[2]


def _minimal_package() -> dict[str, object]:
    return {
        "schema_version": "automation.work_package_plan.v1",
        "work_package_id": "AUTO-TEST-001",
        "work_package_revision": "1",
        "status": "PLANNED_NOT_AUTHORIZED",
        "program_id": "AUTO-TEST-PROGRAM",
        "planning_baseline_sha": "a" * 40,
        "wave": "W1",
        "title": "Contract test",
        "risk": "LOW",
        "depends_on": [],
        "purpose": "Validate the contract",
        "authorization": {"codex_execution": "NOT_AUTHORIZED"},
        "side_effect_envelope": {"network": "DENY"},
        "planned_write_scope": ["tests/example.py"],
        "protected_scope": ["runtime"],
        "acceptance_tests": ["schema parsing"],
        "cost_forecast": {"p90_tokens": 100},
        "telemetry": {"required": True},
        "git_policy": {"force_push": "DENY"},
        "review_barrier": "REQUIRED",
    }


def test_valid_schema_parsing() -> None:
    record = WorkPackageRecord.model_validate(_minimal_package())

    assert record.work_package_id == "AUTO-TEST-001"
    assert record.depends_on == ()
    assert record.authorization["codex_execution"] == "NOT_AUTHORIZED"


def test_missing_required_field_fails_closed() -> None:
    payload = _minimal_package()
    del payload["work_package_id"]

    with pytest.raises(ValidationError):
        WorkPackageRecord.model_validate(payload)


def test_unknown_field_fails_closed() -> None:
    payload = _minimal_package()
    payload["unreviewed_authority"] = True

    with pytest.raises(ValidationError):
        WorkPackageRecord.model_validate(payload)


def test_loaded_model_and_nested_sections_are_read_only() -> None:
    record = WorkPackageRecord.model_validate(_minimal_package())

    with pytest.raises(ValidationError):
        record.status = "AUTHORIZED"  # type: ignore[misc]
    assert isinstance(record.authorization, MappingProxyType)
    with pytest.raises(TypeError):
        record.authorization["codex_execution"] = "AUTHORIZED"  # type: ignore[index]


@pytest.mark.parametrize("document", ["- not\n- a\n- mapping\n", "plain scalar\n"])
def test_safe_loader_rejects_non_mapping_top_level(
    tmp_path: Path, document: str
) -> None:
    source = tmp_path / "invalid.yaml"
    source.write_text(document, encoding="utf-8")

    with pytest.raises(AutomationYamlError, match="top level must be a mapping"):
        load_yaml_mapping(source)


def test_safe_loader_rejects_unsafe_yaml_tag(tmp_path: Path) -> None:
    source = tmp_path / "unsafe.yaml"
    source.write_text(
        "!!python/object/apply:os.system ['echo unsafe']\n", encoding="utf-8"
    )

    with pytest.raises(AutomationYamlError, match="invalid safe YAML"):
        load_yaml_mapping(source)


def test_unknown_schema_fails_closed(tmp_path: Path) -> None:
    source = tmp_path / "unknown.yaml"
    source.write_text("schema_version: automation.unknown.v1\n", encoding="utf-8")

    with pytest.raises(AutomationYamlError, match="unsupported automation schema_version"):
        load_yaml_contract(source)


@pytest.mark.parametrize(
    ("relative_path", "expected_type"),
    [
        ("automation/governance/master_manifest.v1.yaml", MasterManifest),
        (
            "automation/authorizations/AUTH-AUTO-IMP-001-01.v1.yaml",
            AuthorizationRecord,
        ),
        ("automation/packages/AUTO-IMP-001.yaml", WorkPackageRecord),
        (
            "automation/policies/authorization_lifecycle.v1.yaml",
            AuthorizationLifecyclePolicy,
        ),
        (
            "automation/policies/quota_admission_policy.v1_1.yaml",
            QuotaAdmissionPolicy,
        ),
        (
            "automation/policies/development_state_machine.v1.yaml",
            DevelopmentStateMachinePolicy,
        ),
        (
            "automation/policies/development_entry_protocol.v1.yaml",
            DevelopmentEntryProtocol,
        ),
        (
            "automation/programs/AUTO-IMP-PROGRAM-V1/program.yaml",
            ImplementationProgram,
        ),
    ],
)
def test_representative_canonical_contracts_load(
    relative_path: str, expected_type: type[object]
) -> None:
    loaded = load_yaml_contract(ROOT / relative_path)

    assert isinstance(loaded, expected_type)
