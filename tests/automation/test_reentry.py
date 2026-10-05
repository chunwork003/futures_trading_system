from __future__ import annotations

from dataclasses import FrozenInstanceError
from copy import deepcopy
from pathlib import Path
import subprocess

import pytest
import yaml

from automation.engine.manifest import ManifestIntegrityError
from automation.engine.reentry import resolve_reentry
import automation.engine.reentry as reentry_module


ROOT = Path(__file__).resolve().parents[2]
CURRENT = "automation/work_orders/CURRENT_CODEX.yaml"
WORK = "automation/work_orders/WO-AUTO-IMP-002-01.yaml"
AUTH = "automation/authorizations/AUTH-AUTO-IMP-002-01.v1.yaml"
STATE = "docs/CURRENT_STATE.md"
QUOTA = "automation/work_orders/AMEND-AUTO-IMP-002-QUOTA-01.yaml"
ELIGIBILITY = "automation/work_orders/AUTO-IMP-002.eligibility.json"
PACKAGE = "automation/packages/AUTO-IMP-002.yaml"
DEPENDENCY = "automation/work_orders/AUTO-IMP-001.closure.yaml"

# 每列只改一個欄位；其餘 documents 保持有效，覆蓋 reviewer 全部 binding classes。
BINDING_MUTATIONS = [
    (doc, (field,), value)
    for doc in (CURRENT, WORK)
    for field, value in [
        ("work_order_id", "WO-OTHER"), ("package_id", "AUTO-OTHER"),
        ("package_revision", "2"), ("authorization_id", "AUTH-OTHER"),
        ("authorization_revision", "2"), ("exact_write_scope", ["other.py"]),
        ("execution_branch", "auto/other"), ("authorization_state", "RESERVED"),
        ("execution_eligibility", "ELIGIBLE_FOR_AUTOMATIC_TRIGGER"),
    ]
] + [
    (doc, ("quota_amendment", key), value)
    for doc in (CURRENT, WORK)
    for key, value in [("amendment_id", "AMEND-OTHER"), ("status", "REVOKED"), ("effect", "SCOPE_EXPANSION")]
] + [
    (QUOTA, ("exact_binding", key), value)
    for key, value in [
        ("work_order_id", "WO-OTHER"), ("package_id", "AUTO-OTHER"),
        ("package_revision", "2"), ("work_order_path", "automation/other.yaml"),
        ("base_authorization_id", "AUTH-OTHER"), ("base_authorization_revision", "2"),
        ("base_authorization_path", "automation/other.yaml"),
        ("executor_profile", "AUTOMATIC_EXECUTOR"),
    ]
] + [
    (ELIGIBILITY, (key,), value)
    for key, value in [
        ("work_order_id", "WO-OTHER"), ("package_id", "AUTO-OTHER"),
        ("authorization_id", "AUTH-OTHER"), ("package_revision", "2"),
        ("authorization_revision", "2"), ("status", "NOT_ELIGIBLE"),
        ("trigger_mode", "AUTOMATIC_TRIGGER"), ("automatic_dispatch", True),
        ("automatic_next_package", True),
    ]
] + [
    (AUTH, ("authorization_id",), "AUTH-OTHER"),
    (AUTH, ("authorization_revision",), "2"),
    (AUTH, ("exact_binding", "work_package_id"), "AUTO-OTHER"),
    (AUTH, ("exact_binding", "work_package_revision"), "2"),
    (AUTH, ("exact_binding", "allowed_executor_profile"), "AUTOMATIC_EXECUTOR"),
    (AUTH, ("exact_binding", "scope_digest"), "0" * 64),
    (AUTH, ("exact_binding", "review_barrier"), "NONE"),
    (AUTH, ("package_binding", "git_blob_sha"), "0" * 40),
    (AUTH, ("package_binding", "planned_write_scope"), ["other.py"]),
    (AUTH, ("package_binding", "package_revision"), "2"),
    (AUTH, ("program_binding", "package_dependency"), "AUTO-OTHER_ACCEPTED_MATERIALIZED"),
    (PACKAGE, ("work_package_id",), "AUTO-OTHER"),
    (PACKAGE, ("work_package_revision",), "2"),
    (PACKAGE, ("planned_write_scope",), ["other.py"]),
    (DEPENDENCY, ("package_id",), "AUTO-OTHER"),
    (DEPENDENCY, ("status",), "PENDING_REVIEW"),
    (QUOTA, ("amendment_id",), "AMEND-OTHER"),
    (QUOTA, ("status",), "REVOKED"),
    (QUOTA, ("quota", "admission_gate"), "UNBOUNDED"),
    (QUOTA, ("effect", "quota_admission_blocker_only"), False),
    (QUOTA, ("effect", "effective_scope"), "ALL_WORK_ORDERS"),
    (QUOTA, ("effect", "authorization_replay"), True),
    (QUOTA, ("quota", "provider_enforced_limits_waived"), True),
]


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.PIPE)


def _seed_repository(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-b", "master")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    git(tmp_path, "config", "user.name", "Fixture")
    git(tmp_path, "config", "core.autocrlf", "false")
    paths = {"AGENTS.md", STATE, "docs/CURRENT_WORK.md", CURRENT,
             "automation/work_orders/CURRENT_CODEX_TASK.md",
             "automation/governance/master_manifest.v1.yaml"}
    queue = list(paths)
    while queue:
        path = queue.pop()
        blob = git(ROOT, "show", "HEAD:" + path)
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
        if not path.endswith((".yaml", ".json")):
            continue

        def collect(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    if (key == "path" or key.endswith("_path")) and isinstance(item, str) and "/" in item and item not in paths:
                        paths.add(item)
                        queue.append(item)
                    else:
                        collect(item)
            elif isinstance(value, list):
                for item in value:
                    collect(item)

        collect(yaml.safe_load(blob))
    git(tmp_path, "add", "--", *sorted(paths))
    git(tmp_path, "commit", "-m", "fixture")
    return tmp_path


@pytest.fixture(scope="session")
def binding_template(tmp_path_factory) -> Path:
    return _seed_repository(tmp_path_factory.mktemp("binding-template"))


@pytest.fixture
def repository(tmp_path: Path, binding_template: Path) -> Path:
    git(tmp_path, "clone", "--no-hardlinks", str(binding_template), ".")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    git(tmp_path, "config", "user.name", "Fixture")
    git(tmp_path, "config", "core.autocrlf", "false")
    return tmp_path


def change(repository: Path, path: str, key: str, value: object) -> None:
    source = repository / path
    payload = yaml.safe_load(source.read_bytes())
    payload[key] = value
    source.write_text(yaml.safe_dump(payload), encoding="utf-8")
    git(repository, "add", "--", path)
    git(repository, "commit", "-m", "fixture change")


def test_repository_answer_prevents_reask_and_never_dispatches(repository: Path) -> None:
    before = git(repository, "status", "--porcelain")
    head = git(repository, "rev-parse", "HEAD")
    snapshot = resolve_reentry(repository, "HEAD")
    assert snapshot.route == "CODEX_EXECUTION_CANDIDATE"
    assert snapshot.current_state["development_automation_current_package"] == "AUTO-IMP-002"
    assert snapshot.stop_reason is None
    assert snapshot.execution_allowed is False
    assert "CLAIM_REQUIRED" in snapshot.next_action
    assert git(repository, "rev-parse", "HEAD") == head
    assert git(repository, "status", "--porcelain") == before
    assert git(repository, "branch", "--list", "auto/*") == b""


def test_status_only_no_execution(repository: Path) -> None:
    result = resolve_reentry(repository, "HEAD", status_only=True)
    assert result.next_action == "REPORT_CURRENT_STATE_WITHOUT_EXECUTION"
    assert result.execution_allowed is False


def test_snapshot_is_deeply_read_only(repository: Path) -> None:
    result = resolve_reentry(repository, "HEAD")
    with pytest.raises(FrozenInstanceError):
        result.route = "ACCEPTED"
    with pytest.raises(TypeError):
        result.documents[CURRENT]["status"] = "ACCEPTED"
    with pytest.raises(TypeError):
        result.current_state["next"] = "EXECUTE"


def test_historical_state_does_not_override_canonical(repository: Path) -> None:
    path = repository / STATE
    with path.open("a", encoding="utf-8") as stream:
        stream.write("\n```text\ndevelopment_automation_current_package = OLD\nnext = OLD\n```\n")
    git(repository, "add", STATE)
    git(repository, "commit", "-m", "history")
    assert resolve_reentry(repository, "HEAD").route == "CODEX_EXECUTION_CANDIDATE"


def test_duplicate_canonical_state_rejected(repository: Path) -> None:
    path = repository / STATE
    path.write_text(path.read_text(encoding="utf-8").replace("branch = master", "branch = master\nbranch = master", 1), encoding="utf-8")
    git(repository, "add", STATE)
    git(repository, "commit", "-m", "ambiguous current")
    with pytest.raises(ManifestIntegrityError, match="ambiguous"):
        resolve_reentry(repository, "HEAD")


@pytest.mark.parametrize("status,route", [("COMPLETED_PENDING_REVIEW", "PENDING_REVIEW"), ("STOPPED", "STOP")])
def test_exact_open_handoff_has_priority(repository: Path, status: str, route: str) -> None:
    path = "automation/handoff.yaml"
    (repository / path).write_text(yaml.safe_dump({"status": status}), encoding="utf-8")
    git(repository, "add", path)
    git(repository, "commit", "-m", "handoff")
    result = resolve_reentry(repository, "HEAD", handoff_paths=(path,))
    assert result.route == route
    assert result.execution_allowed is False


def test_pointer_binding_mismatch_stops(repository: Path) -> None:
    change(repository, WORK, "package_id", "AUTO-IMP-003")
    result = resolve_reentry(repository, "HEAD")
    assert result.route == "STOP"
    assert result.stop_reason == "CURRENT_WORK_ORDER_BINDING_MISMATCH"


def test_consumed_authorization_cannot_be_replayed(repository: Path) -> None:
    change(repository, AUTH, "authorization_state", "CONSUMED")
    result = resolve_reentry(repository, "HEAD")
    assert result.route == "STOP"
    assert result.stop_reason == "AUTHORIZATION_NOT_AVAILABLE"


def test_integrity_failure_blocks_candidate(repository: Path) -> None:
    (repository / "AGENTS.md").write_text("changed", encoding="utf-8")
    git(repository, "add", "AGENTS.md")
    git(repository, "commit", "-m", "tamper")
    result = resolve_reentry(repository, "HEAD")
    assert result.route == "STOP"
    assert result.stop_reason == "MANIFEST_INTEGRITY_MISMATCH"


def test_pinned_snapshot_ignores_uncommitted_authority(repository: Path) -> None:
    (repository / AUTH).write_text("malformed", encoding="utf-8")
    assert resolve_reentry(repository, "HEAD").route == "CODEX_EXECUTION_CANDIDATE"


def test_review_counterexample_amendment_identity_stops(repository: Path) -> None:
    """RF01 reviewer 反例：只改 CURRENT id，仍指向原有效 amendment。"""
    payload = yaml.safe_load((repository / CURRENT).read_bytes())
    original_path = payload["quota_amendment"]["path"]
    payload["quota_amendment"]["amendment_id"] = "AMEND-OTHER"
    (repository / CURRENT).write_text(yaml.safe_dump(payload), encoding="utf-8")
    git(repository, "add", CURRENT)
    git(repository, "commit", "-m", "review counterexample")
    result = resolve_reentry(repository, "HEAD")
    assert original_path in result.documents
    assert result.route == "STOP"
    assert result.execution_allowed is False


@pytest.mark.parametrize("document,fields,value", BINDING_MUTATIONS,
                         ids=[p.split("/")[-1] + ":" + ".".join(f) for p, f, _ in BINDING_MUTATIONS])
def test_cross_artifact_negative_binding_matrix(repository: Path, document: str,
                                                fields: tuple[str, ...], value: object) -> None:
    payload = yaml.safe_load((repository / document).read_bytes())
    section = payload
    for field in fields[:-1]:
        section = section[field]
    section[fields[-1]] = value
    (repository / document).write_text(yaml.safe_dump(payload), encoding="utf-8")
    git(repository, "add", document)
    git(repository, "commit", "-m", "single field binding mutation")
    result = resolve_reentry(repository, "HEAD")
    assert result.route == "STOP"
    assert result.stop_reason is not None
    assert result.execution_allowed is False


@pytest.mark.parametrize("document,fields,target", [
    (CURRENT, ("authorization_path",), AUTH), (WORK, ("authorization_path",), AUTH),
    (CURRENT, ("eligibility_path",), ELIGIBILITY), (WORK, ("eligibility_path",), ELIGIBILITY),
    (CURRENT, ("quota_amendment", "path"), QUOTA), (WORK, ("quota_amendment", "path"), QUOTA),
    (AUTH, ("package_binding", "path"), PACKAGE),
    (AUTH, ("program_binding", "dependency_closure_path"), DEPENDENCY),
])
def test_valid_duplicate_document_cannot_hide_wrong_pointer(repository: Path, document: str,
                                                          fields: tuple[str, ...], target: str) -> None:
    alias = "automation/alias.yaml"
    (repository / alias).write_bytes((repository / target).read_bytes())
    payload = yaml.safe_load((repository / document).read_bytes())
    section = payload
    for field in fields[:-1]:
        section = section[field]
    section[fields[-1]] = alias
    (repository / document).write_text(yaml.safe_dump(payload), encoding="utf-8")
    git(repository, "add", document, alias)
    git(repository, "commit", "-m", "valid document wrong pointer")
    result = resolve_reentry(repository, "HEAD")
    assert result.route == "STOP"
    assert result.execution_allowed is False


@pytest.fixture(scope="module")
def effect_documents():
    """RF02 純語意基準：不為每個 effect 反例 clone/commit repository。"""
    paths = [CURRENT, WORK, AUTH, QUOTA, ELIGIBILITY, PACKAGE, DEPENDENCY]
    payloads = [yaml.safe_load((ROOT / path).read_bytes()) for path in paths]
    state = reentry_module._current_projection((ROOT / STATE).read_text(encoding="utf-8"))
    return state, payloads


@pytest.mark.parametrize("case", ["side_effect_expansion", "next_package_authority", "provider_hard_block"])
def test_rf02_execution_effect_counterexamples(effect_documents, monkeypatch, case: str) -> None:
    state, baseline = effect_documents
    # Package blob identity 已由 Git integration suite 覆蓋；本組只測 effect。
    monkeypatch.setattr(reentry_module, "_git", lambda *_: baseline[2]["package_binding"]["git_blob_sha"].encode())
    if case == "side_effect_expansion":
        variants = [(1, ("side_effects", key), "ALLOW")
                    for key in ("runtime", "broker", "db", "migration", "live", "production")]
    elif case == "next_package_authority":
        variants = [(0, ("auto_imp_003_authorized",), True),
                    (1, ("next_package", "package_id"), "AUTO-OTHER"),
                    (1, ("next_package", "authorization"), "AUTHORIZED")]
    else:
        variants = [(index, ("quota_gate", "provider_hard_block"), "IGNORE") for index in (0, 1)]
    for index, fields, value in variants:
        documents = deepcopy(baseline)
        section = documents[index]
        for field in fields[:-1]:
            section = section[field]
        section[fields[-1]] = value
        with pytest.raises(ValueError):
            reentry_module._validate_bindings(ROOT, "unused-pure-case", state, *documents)
