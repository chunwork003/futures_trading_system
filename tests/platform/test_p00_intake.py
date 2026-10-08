"""缺項不是 NONE；規格路由不能冒充 resume／dispatch 權限。"""

from copy import deepcopy
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError

from scripts.p00_intake import ORDER, propose

SCHEMA = json.loads((Path(__file__).resolve().parents[2] / "automation/platform/intake_observation.schema.v1.json").read_text(encoding="utf-8"))


def fixture():
    reference = {"path": "registry.json", "git_blob": "a" * 40, "sha256": "b" * 64, "json_pointer": "/empty"}
    return {"schema_version": "p00.intake_observation.v1", "authority": "NONE_PLANNING_ONLY",
            "execution_eligible": False, "source_master": "c" * 40,
            "observations": {name: {"knowledge": "NONE", "scope": "CURRENT_PROGRAM", "items": [],
                                    "evidence": [deepcopy(reference)], "reason": "synthetic explicit none"}
                             for name, _ in ORDER}}


@pytest.mark.parametrize("field,action", ORDER)
def test_first_present_work_precedes_unrelated_work(field, action):
    value = fixture()
    value["observations"][field].update(knowledge="PRESENT", items=["exact-id"])
    result = propose(value, SCHEMA)
    assert result["proposal"] == action
    assert result["execution_eligible"] is False
    assert result["evidence_trust_verified"] is False


def test_unknown_stop_blocks_known_result_and_does_not_fabricate_resume():
    value = fixture()
    value["observations"]["stop"].update(knowledge="UNKNOWN", evidence=[])
    value["observations"]["active_execution"].update(knowledge="PRESENT", items=["consumed-but-not-invoked"])
    assert propose(value, SCHEMA)["reason"] == "stop"
    value["observations"]["stop"] = fixture()["observations"]["stop"]
    assert propose(value, SCHEMA)["proposal"] == "REVALIDATE_EXECUTION_LINEAGE"


def test_all_none_only_proposes_authority_evaluation():
    assert propose(fixture(), SCHEMA)["proposal"] == "EVALUATE_AUTHORITY_AND_DEPENDENCIES"


@pytest.mark.parametrize("mutation", [
    lambda v: v["observations"].pop("pending_review"),
    lambda v: v["observations"]["stop"].update(evidence=[]),
    lambda v: v["observations"]["stop"].update(knowledge="PRESENT"),
    lambda v: v["observations"]["stop"].update(scope="SINGLE_PACKAGE"),
    lambda v: v.update(execution_eligible=True),
])
def test_missing_or_unproven_empty_or_narrow_scope_rejected(mutation):
    value = fixture()
    mutation(value)
    with pytest.raises(ValidationError):
        propose(value, SCHEMA)
