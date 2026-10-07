"""候選 DTO 形狀與雙層 API 隔離負例；不宣稱 runtime conformance。"""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[2]
SPEC = json.loads((ROOT / "docs/architecture/contracts/python.openapi.v1.json").read_text(encoding="utf-8"))
BFF = json.loads((ROOT / "docs/architecture/contracts/bff.openapi.v1.json").read_text(encoding="utf-8"))


def validate(name, value):
    schema = {"$ref": f"#/components/schemas/{name}", "components": SPEC["components"]}
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)


def request_example(path):
    return deepcopy(SPEC["paths"][path]["post"]["requestBody"]["content"]["application/json"]["examples"]["synthetic"]["value"])


def test_generated_specs_have_no_drift():
    module_spec = importlib.util.spec_from_file_location("p00_generator", ROOT / "scripts/p00_build_contracts.py")
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    for name, expected in module.build().items():
        assert json.loads((ROOT / "docs/architecture/contracts" / name).read_text(encoding="utf-8")) == expected


def test_all_schema_refs_resolve_locally_and_examples_validate():
    def visit(value):
        if isinstance(value, dict):
            if "$ref" in value:
                assert value["$ref"].startswith("#/")
                target = SPEC
                for component in value["$ref"][2:].split("/"):
                    target = target[component]
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    visit(SPEC)
    for schema in SPEC["components"]["schemas"].values():
        Draft202012Validator.check_schema(schema)
    for path in SPEC["paths"].values():
        for operation in path.values():
            containers = ([operation["requestBody"]] if "requestBody" in operation else [])
            containers += [r for r in operation["responses"].values() if "application/json" in r.get("content", {})]
            for container in containers:
                media = next(iter(container["content"].values()))
                name = media["schema"]["$ref"].split("/")[-1]
                for sample in media["examples"].values():
                    validate(name, sample["value"])


@pytest.mark.parametrize("value", [1.5, "1e3", "NaN", "Infinity", "-0", "00", "+1", "1.0", "0.00", " 1"])
def test_money_rejects_noncanonical_wire_values(value):
    with pytest.raises(ValidationError):
        validate("Decimal", value)


@pytest.mark.parametrize("value", ["0", "1", "-1", "0.01", "-123.456"])
def test_money_accepts_normalized_fixed_point(value):
    validate("Decimal", value)


@pytest.mark.parametrize("value", ["0", "-1", "-0.01"])
def test_genesis_capital_must_be_positive(value):
    request = request_example("/api/v1/research-runs")
    request["initial_capital"] = value
    from jsonschema import ValidationError
    with pytest.raises(ValidationError):
        validate("ResearchRunRequest", request)


@pytest.mark.parametrize("mode", ["LIVE", "LIVE_AUTO", "BROKER_PAPER", "BACKTEST"])
def test_simulation_does_not_accept_live_or_broker_mode(mode):
    request = request_example("/api/v1/simulation-sessions")
    request["mode"] = mode
    from jsonschema import ValidationError
    with pytest.raises(ValidationError):
        validate("SimulationRequest", request)


def test_unknown_actual_cannot_smuggle_empty_positions():
    schema_name = "AccountState"
    sample = deepcopy(SPEC["paths"]["/api/v1/accounts/{id}/state"]["get"]["responses"]["200"]["content"]["application/json"]["examples"]["synthetic"]["value"])
    sample["actual"] = {"status": "UNKNOWN", "reason_code": "MISSING_OBSERVATION"}
    validate(schema_name, sample)
    sample["actual"]["positions"] = []
    from jsonschema import ValidationError
    with pytest.raises(ValidationError):
        validate(schema_name, sample)


def test_closed_request_rejects_missing_identity_and_extra_authority():
    from jsonschema import ValidationError
    request = request_example("/api/v1/research-runs")
    request["authorized"] = True
    with pytest.raises(ValidationError):
        validate("ResearchRunRequest", request)
    del request["authorized"]
    del request["bindings"]["dataset"]["identity"]
    with pytest.raises(ValidationError):
        validate("ResearchRunRequest", request)


def test_authentication_surfaces_cannot_be_used_interchangeably():
    assert SPEC["security"] == [{"ServiceToken": []}]
    assert BFF["security"] == [{"OperatorCookie": []}]
    assert set(SPEC["components"]["securitySchemes"]) == {"ServiceToken"}
    assert set(BFF["components"]["securitySchemes"]) == {"OperatorCookie"}
    operation_ids = []
    for path, methods in SPEC["paths"].items():
        for method, operation in methods.items():
            operation_ids.append(operation["operationId"])
            browser = BFF["paths"][path][method]
            assert "security" not in operation and "security" not in browser
            if method == "post":
                assert {"$ref": "#/components/parameters/IdempotencyKey"} in operation["parameters"]
                assert {"$ref": "#/components/parameters/Csrf"} in browser["parameters"]
                assert {"$ref": "#/components/parameters/Csrf"} not in operation["parameters"]
                if "{id}" in path:
                    assert {"$ref": "#/components/parameters/IfMatch"} in operation["parameters"]
            assert set(operation["x-contract"]) == {"owner", "permission", "authority", "transaction", "async",
                "idempotency", "expected_revision", "retry", "cancellation", "pagination", "audit"}
    assert len(operation_ids) == len(set(operation_ids))


def test_profile_has_finite_consistent_aggregate_limits():
    profile = json.loads((ROOT / "docs/architecture/contracts/workload_policy.v1.json").read_text(encoding="utf-8"))
    assert 0 < profile["heartbeat_seconds"] * 2 < profile["lease_seconds"]
    assert profile["max_artifact_bytes"] <= profile["max_run_artifact_bytes"]
    assert profile["default_page_size"] <= profile["max_page_size"] <= 1000
    assert profile["max_monte_carlo_paths"] * profile["max_monte_carlo_source_returns"] <= profile["max_monte_carlo_samples"]
    assert len(profile["transient_retry_delays_seconds"]) == 2
    for key, value in profile.items():
        if key.startswith("max_"):
            assert type(value) is int and 0 < value <= 2**40
