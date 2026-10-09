"""R06 source/session/omission counterexamples；不將合成已讀聲明冒充qualification。"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError

from scripts import p00_reading as reading
from scripts.p00_context import canonical
from scripts.p00_context_pack import encode_document

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / reading.SCHEMA).read_text(encoding="utf-8"))


def inputs():
    # JSON whitespace壓縮可讓閱讀pack低於target，原source仍超限。
    raw = b" " * 140000 + b'{"security":["deny"],"required":["authority"]}'
    ref = {"path": "contract.json", "baseline_sha": "a" * 40, "git_blob": "b" * 40,
           "sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw)}
    request = {"task_type": "CODEX", "package_id": "P01", "changed_paths": ["storage/dataset_import.py"],
               "architecture_domains": [], "baseline_sha": "a" * 40}
    context = {"authority": "NONE_CONTEXT_ONLY", "execution_eligible": False, "request": request,
               "source_baseline_sha": "c" * 40, "context_hash": "d" * 64,
               "mandatory_context": [ref], "context_budget": {"mandatory_bytes": len(raw), "target_max_bytes": 131072}}
    pack = {"authority": "NONE_READING_AID_ONLY", "execution_eligible": False,
            "request": request, "source_baseline_sha": "c" * 40, "source_context_hash": "d" * 64,
            "documents": [{"source": ref, **encode_document(ref["path"], raw, {})}], "schema_pool": {}}
    consumer = {"role": "CODEX", "task_id": "task-1", "session_id": "session-1", "continuity_epoch": 1}
    return context, pack, consumer


def plan_and_claim():
    context, pack, consumer = inputs()
    plan = reading.make_plan(context, canonical(pack), consumer, SCHEMA)
    claim = {"schema_version": "p00.reading_claim.v1", "status": "CLAIM_ONLY", "consumer": consumer,
             "plan_hash": plan["plan_hash"], "obligation_id": plan["obligations"][0]["id"],
             "payload_sha256": plan["obligations"][0]["payload_sha256"]}
    return plan, claim, consumer


def test_all_claims_and_small_pack_never_clear_original_budget_or_trust():
    plan, claim, consumer = plan_and_claim()
    result = reading.audit_claims(plan, [claim], consumer, SCHEMA)
    assert result["status"] == "ALL_PAYLOADS_CLAIMED_NOT_VERIFIED"
    assert plan["representation_fits_target"] is True
    assert plan["original_budget"]["status"] == "OVER_TARGET_REQUIRES_COMPACTION"
    assert result["actual_reading_verified"] is False
    assert result["current_intake_complete"] is False
    assert result["execution_eligible"] is False
    assert result["semantic_qualification"] == "NOT_PERFORMED"


def test_empty_claims_keep_every_obligation_missing_and_exact_replay_dedupes():
    plan, claim, consumer = plan_and_claim()
    assert reading.audit_claims(plan, [], consumer, SCHEMA)["missing"] == [claim["obligation_id"]]
    result = reading.audit_claims(plan, [claim, deepcopy(claim)], consumer, SCHEMA)
    assert result["duplicates"] == 1 and len(result["claimed"]) == 1
    assert result["trust"] == "UNVERIFIED_CALLER_CLAIMS"


def test_conflicting_replay_cannot_overwrite_receipt():
    plan, claim, consumer = plan_and_claim()
    bad = {**claim, "payload_sha256": "e" * 64}
    with pytest.raises(ValueError, match="READING_CLAIM_CONFLICT"):
        reading.audit_claims(plan, [claim, bad], consumer, SCHEMA)


@pytest.mark.parametrize("field,value", [("task_id", "task-2"), ("session_id", "session-2"),
                                        ("continuity_epoch", 2), ("role", "REVIEWER")])
def test_consumer_or_context_loss_requires_reread_even_without_claims(field, value):
    plan, claim, consumer = plan_and_claim()
    changed = {**consumer, field: value}
    with pytest.raises(ValueError, match="SESSION_OR_CONSUMER_CHANGED_REREAD"):
        reading.audit_claims(plan, [claim], changed, SCHEMA)
    with pytest.raises(ValueError):
        reading.audit_claims(plan, [], changed, SCHEMA)


@pytest.mark.parametrize("field,value,reason", [("plan_hash", "f" * 64, "STALE_PLAN"),
    ("payload_sha256", "f" * 64, "PAYLOAD_CHANGED"), ("obligation_id", "read:missing.json", "UNKNOWN_READING")])
def test_source_or_representation_mismatch_is_not_silently_acknowledged(field, value, reason):
    plan, claim, consumer = plan_and_claim()
    with pytest.raises(ValueError, match=reason):
        reading.audit_claims(plan, [{**claim, field: value}], consumer, SCHEMA)


@pytest.mark.parametrize("field,value", [("status", "ACCEPTED"), ("execution_eligible", True),
                                        ("trusted", True), ("review_status", "PASS")])
def test_claim_cannot_add_authority_or_trust_fields(field, value):
    plan, claim, consumer = plan_and_claim()
    with pytest.raises(ValidationError):
        reading.audit_claims(plan, [{**claim, field: value}], consumer, SCHEMA)


@pytest.mark.parametrize("epoch", [True, False, 1.0, 0, -1])
def test_epoch_must_be_true_positive_json_integer(epoch):
    context, pack, consumer = inputs()
    with pytest.raises((ValueError, ValidationError)):
        reading.make_plan(context, canonical(pack), {**consumer, "continuity_epoch": epoch}, SCHEMA)


@pytest.mark.parametrize("change", ["missing", "duplicate", "source", "context", "budget", "grant"])
def test_manifest_omission_or_rebinding_cannot_make_read_plan(change):
    context, pack, consumer = inputs()
    if change == "missing": pack["documents"] = []
    if change == "duplicate": pack["documents"] *= 2
    if change == "source": pack["documents"][0]["source"] = {**pack["documents"][0]["source"], "git_blob": "e" * 40}
    if change == "context": pack["source_context_hash"] = "e" * 64
    if change == "budget": context["context_budget"]["target_max_bytes"] *= 2
    if change == "grant": pack["execution_eligible"] = True
    with pytest.raises(ValueError): reading.make_plan(context, canonical(pack), consumer, SCHEMA)


def test_projection_exclusions_and_archive_remain_unreviewed():
    context, pack, consumer = inputs()
    pack["documents"][0]["projection"] = {"excluded_paths": ["/safety"], "excluded_schemas": ["Auth"]}
    plan = reading.make_plan(context, canonical(pack), consumer, SCHEMA)
    obligation = plan["obligations"][0]
    assert obligation["exclusions"]["excluded_paths"] == ["/safety"]
    assert obligation["semantic_discharge"] == "NOT_REVIEWED"
    assert obligation["mode"] == "JSON_PROJECTION"


def test_scope_change_invalidates_prior_claim_even_after_valid_plan_rehash():
    plan, claim, consumer = plan_and_claim()
    changed = deepcopy(plan)
    changed["request"]["changed_paths"].append("storage/dataset_manifest.py")
    changed["plan_hash"] = reading.digest({k: v for k, v in changed.items() if k != "plan_hash"})
    with pytest.raises(ValueError, match="STALE_PLAN"):
        reading.audit_claims(changed, [claim], consumer, SCHEMA)


def test_plan_edit_without_rehash_and_input_aliasing():
    plan, claim, consumer = plan_and_claim()
    before = deepcopy((plan, claim, consumer))
    reading.audit_claims(plan, [claim], consumer, SCHEMA)
    assert (plan, claim, consumer) == before
    plan["original_budget"]["status"] = "WITHIN_TARGET"
    with pytest.raises(ValueError, match="PLAN_HASH_MISMATCH"):
        reading.audit_claims(plan, [claim], consumer, SCHEMA)


# 共用既有隔離 Git fixture；沒有產品／control-plane 寫入。
from test_p00_context import repository, write, commit


def test_bound_source_reconstruction_rejects_forged_and_stale_claims(repository):
    from scripts.p00_context_pack import PACKER_PATH, SELECTION_PATH, MARKER
    root, request = repository
    for path in [reading.TOOL, reading.CONTRACT, reading.SCHEMA, PACKER_PATH]:
        write(root, path, (ROOT / path).read_text(encoding="utf-8"))
    write(root, SELECTION_PATH, {"status": "CANDIDATE_READING_ONLY", "packages": {"P00": {}}})
    for path in ["docs/CURRENT_STATE.md", "docs/CURRENT_WORK.md"]:
        write(root, path, "# CURRENT\nDENY\n" + MARKER + "\nhistory\n")
    manifest = json.loads((root / "automation/governance/master_manifest.v1.yaml").read_text(encoding="utf-8"))
    negative_path = "automation/specs/negative_assertions.fixture.json"
    write(root, negative_path, "deny")
    manifest["negative_assertions"] = {"path": negative_path, "active": True,
                                       "sha256": hashlib.sha256(b"deny").hexdigest()}
    write(root, "automation/governance/master_manifest.v1.yaml", manifest)
    request["baseline_sha"] = commit(root)
    consumer = {"role": "ARCHITECT", "task_id": "fixture", "session_id": "fixture", "continuity_epoch": 1}
    first = reading.inspect_bound(root, request, consumer, [], request["baseline_sha"])
    plan = first["plan"]
    assert plan["source_validation"] == "REGENERATED_EXACT_SOURCE_REVIEW_NOT_ASSERTED"
    assert plan["governance_source_coverage"]["status"] == "UNREPRESENTED_DECLARED_GOVERNANCE_SOURCES"
    assert plan["governance_source_coverage"]["unrepresented_sources"][0]["path"] == negative_path
    assert first["audit"]["missing"]
    assert first["carrier_metrics"]["compiler_gate_changed"] is False
    claim = {"schema_version": "p00.reading_claim.v1", "status": "CLAIM_ONLY", "consumer": consumer,
             "plan_hash": plan["plan_hash"], "obligation_id": plan["obligations"][0]["id"],
             "payload_sha256": plan["obligations"][0]["payload_sha256"]}
    write(root, "docs/architecture/V1_CONTRACTS.md", "dirty claiming ready")
    assert reading.inspect_bound(root, request, consumer, [claim], request["baseline_sha"])["plan"] == plan
    request["baseline_sha"] = commit(root)
    with pytest.raises(ValueError, match="STALE_PLAN"):
        reading.inspect_bound(root, request, consumer, [claim], request["baseline_sha"])
    with pytest.raises(ValueError, match="MASTER_DRIFT"):
        reading.inspect_bound(root, request, consumer, [], plan["request"]["baseline_sha"])
    write(root, reading.TOOL, (ROOT / reading.TOOL).read_text(encoding="utf-8") + "\n# changed loaded tool\n")
    request["baseline_sha"] = commit(root)
    with pytest.raises(ValueError, match="LOADED_TOOL_SOURCE_MISMATCH"):
        reading.inspect_bound(root, request, consumer, [], request["baseline_sha"])
