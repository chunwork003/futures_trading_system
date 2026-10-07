"""平台 registry 的角色/side-effect 宣告不能自行升級為 authority。"""

from copy import deepcopy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

BASE = Path(__file__).resolve().parents[2] / "automation/platform"


@pytest.mark.parametrize("name,key", [("agent", "agents"), ("tool", "tools")])
def test_registry_shape_and_unique_ids(name, key):
    schema = json.loads((BASE / f"{name}_registry.schema.v1.json").read_text(encoding="utf-8"))
    registry = json.loads((BASE / f"{name}_registry.v1.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    validator.validate(registry)
    assert len({r["id"] for r in registry[key]}) == len(registry[key])
    promoted = deepcopy(registry)
    promoted["status"] = "AUTHORIZED"
    with pytest.raises(ValidationError):
        validator.validate(promoted)


def test_agents_cannot_be_declared_operationally_qualified_without_schema_revision():
    schema = json.loads((BASE / "agent_registry.schema.v1.json").read_text(encoding="utf-8"))
    registry = json.loads((BASE / "agent_registry.v1.json").read_text(encoding="utf-8"))
    registry["agents"][0]["authority_source"] = "THIS_REGISTRY"
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(registry)


def test_context_request_cannot_smuggle_a_grant():
    schema = json.loads((BASE / "context_request.schema.v1.json").read_text(encoding="utf-8"))
    request = {"task_type": "ARCHITECT", "package_id": "P00", "changed_paths": [],
               "architecture_domains": [], "baseline_sha": "a" * 40}
    validator = Draft202012Validator(schema)
    validator.validate(request)
    request["authorized"] = True
    with pytest.raises(ValidationError):
        validator.validate(request)
