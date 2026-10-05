from __future__ import annotations

from dataclasses import FrozenInstanceError
from copy import deepcopy
from pathlib import Path
import subprocess
import hashlib

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
    # Candidate 完全由測試擁有，不從 mutable master CURRENT 遞迴複製 authority。
    for path, value in candidate_documents().items():
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(value.encode() if isinstance(value, str) else yaml.safe_dump(value).encode())
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-m", "fixture")
    return tmp_path


def candidate_documents() -> dict:
    """固定 READY 契約與 exact package blob；僅 fixture，不建立 repository authority。"""
    scope = ["automation/engine/manifest.py", "automation/engine/reentry.py",
             "tests/automation/test_manifest.py", "tests/automation/test_reentry.py"]
    current = dict(work_order_id="WO-AUTO-IMP-002-01", package_id="AUTO-IMP-002",
                   package_revision="1", authorization_id="AUTH-AUTO-IMP-002-01",
                   authorization_revision="1", authorization_state="AUTHORIZED",
                   exact_write_scope=scope, execution_branch="auto/WO-AUTO-IMP-002-01",
                   authorization_path=AUTH, work_order_path=WORK, eligibility_path=ELIGIBILITY,
                   status="READY_FOR_CODEX", handoff_ready=True, auto_imp_003_authorized=False,
                   execution_eligibility="ELIGIBLE_FOR_MANUAL_TRIGGER_WITH_MANIFEST_INTEGRITY_PASS",
                   quota_gate={"provider_hard_block": "STOP"},
                   quota_amendment=dict(amendment_id="AMEND-AUTO-IMP-002-QUOTA-01", path=QUOTA,
                                        status="AUTHORIZED_EFFECTIVE", effect="EXACT_QUOTA_ADMISSION_ONLY"))
    work = deepcopy(current)
    work.update(side_effects={key: "DENIED" for key in ("runtime", "broker", "db", "migration", "live", "production")},
                next_package=dict(package_id="AUTO-IMP-003", authorization="NOT_AUTHORIZED"))
    package = dict(work_package_id="AUTO-IMP-002", work_package_revision="1",
                   planned_write_scope=scope, depends_on=["AUTO-IMP-001"])
    blob = yaml.safe_dump(package).encode()
    oid = hashlib.sha1(b"blob " + str(len(blob)).encode() + b"\0" + blob).hexdigest()
    auth = dict(authorization_id=current["authorization_id"], authorization_revision="1",
                authorization_state="AUTHORIZED",
                exact_binding=dict(work_package_id="AUTO-IMP-002", work_package_revision="1",
                                   scope_digest=hashlib.sha256("\n".join(scope).encode()).hexdigest(),
                                   allowed_executor_profile="CODEX_SINGLE_EXECUTOR_MANUAL_TRIGGER_ONLY",
                                   review_barrier="REQUIRED_BEFORE_ACCEPTANCE"),
                package_binding=dict(path=PACKAGE, git_blob_sha=oid, planned_write_scope=scope),
                program_binding=dict(package_dependency="AUTO-IMP-001_ACCEPTED_MATERIALIZED",
                                     dependency_closure_path=DEPENDENCY))
    quota = dict(amendment_id="AMEND-AUTO-IMP-002-QUOTA-01", status="AUTHORIZED_EFFECTIVE",
                 decision="WAIVED_FOR_BOUNDED_AUTOMATION_PILOT",
                 exact_binding=dict(work_order_id=current["work_order_id"], package_id="AUTO-IMP-002",
                                    package_revision="1", work_order_path=WORK, base_authorization_path=AUTH,
                                    base_authorization_id=current["authorization_id"], base_authorization_revision="1",
                                    executor_profile="CODEX_SINGLE_EXECUTOR_MANUAL_TRIGGER_ONLY"),
                 effect=dict(quota_admission_blocker_only=True, effective_scope="THIS_EXACT_WORK_ORDER_ONLY",
                             authorization_replay=False, extra_work_order_created=False, automatic_threshold_mutation=False),
                 quota=dict(admission_gate="WAIVED_FOR_BOUNDED_AUTOMATION_PILOT", provider_enforced_limits_waived=False))
    eligibility = dict(work_order_id=current["work_order_id"], package_id="AUTO-IMP-002",
                       authorization_id=current["authorization_id"], status="ELIGIBLE_FOR_MANUAL_TRIGGER",
                       trigger_mode="MANUAL_TRIGGER_ONLY", automatic_dispatch=False, automatic_next_package=False)
    state = "### CURRENT_AUTHORITY_SNAPSHOT\n```text\nbranch = master\n" + "\n".join(
        "development_automation_current_" + key + " = " + value for key, value in
        [("package", "AUTO-IMP-002"), ("authorization_id", current["authorization_id"]),
         ("authorization_revision", "1"), ("authorization_state", "AUTHORIZED")]) + "\n```\n"
    agents = "Fixture navigation; no execution authority.\n"
    sections = ("compiled_program", "compiled_authorization_candidate", "quota_policy_compatibility_rf",
                "freeze", "canonical_current_state", "governance_document", "policies", "negative_assertions", "activation")
    manifest = {key: {} for key in sections}
    manifest.update(schema_version="automation.master_manifest.v1", manifest_id="FIXTURE",
                    manifest_version="1", master_architecture_version="1.1", status="FROZEN",
                    materialization_baseline_sha="0" * 40, superseded_authorization_candidates=[],
                    agent_reentry=dict(path="AGENTS.md", sha256=hashlib.sha256(agents.encode()).hexdigest()),
                    hash_integrity=dict(algorithm="SHA-256", canonical_input="git_blob_bytes",
                                        verification_scope="exact_review_commit", worktree_bytes_are_authoritative=False,
                                        line_ending_normalization="none"))
    return {CURRENT: current, WORK: work, AUTH: auth, QUOTA: quota, ELIGIBILITY: eligibility,
            PACKAGE: package, DEPENDENCY: dict(package_id="AUTO-IMP-001", status="ACCEPTED_MATERIALIZED"),
            STATE: state, "AGENTS.md": agents, "docs/CURRENT_WORK.md": "Fixture queue.\n",
            "automation/work_orders/CURRENT_CODEX_TASK.md": "Fixture task.\n",
            "automation/governance/master_manifest.v1.yaml": manifest}


@pytest.fixture(scope="session")
def binding_template(tmp_path_factory) -> Path:
    return _seed_repository(tmp_path_factory.mktemp("binding-template"))


@pytest.fixture
def repository(tmp_path: Path, binding_template: Path) -> Path:
    git(tmp_path, "-c", "core.autocrlf=false", "clone", "--no-hardlinks", str(binding_template), ".")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    git(tmp_path, "config", "user.name", "Fixture")
    git(tmp_path, "config", "core.autocrlf", "false")
    positive = resolve_reentry(tmp_path, "HEAD")
    assert positive.route == "CODEX_EXECUTION_CANDIDATE" and positive.execution_allowed is False
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
def effect_documents(binding_template):
    """RF02 純語意基準：不為每個 effect 反例 clone/commit repository。"""
    paths = [CURRENT, WORK, AUTH, QUOTA, ELIGIBILITY, PACKAGE, DEPENDENCY]
    positive = resolve_reentry(binding_template, "HEAD")
    assert positive.route == "CODEX_EXECUTION_CANDIDATE" and positive.execution_allowed is False
    payloads = [yaml.safe_load((binding_template / path).read_bytes()) for path in paths]
    state = reentry_module._current_projection((binding_template / STATE).read_text(encoding="utf-8"))
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


@pytest.mark.parametrize("group", ["non_candidate", "missing_package_binding", "missing_program_binding"])
def test_ic01_compatibility_groups(repository: Path, group: str) -> None:
    """三個最小 pre-fix 群組；READY 缺 binding 與 post-execution 必須安全停止。"""
    if group == "non_candidate":
        change(repository, CURRENT, "status", "COMPLETED_PENDING_REVIEW")
        change(repository, WORK, "status", "COMPLETED_PENDING_REVIEW")
    payload = yaml.safe_load((repository / AUTH).read_bytes())
    payload.pop("program_binding" if group == "missing_program_binding" else "package_binding")
    (repository / AUTH).write_text(yaml.safe_dump(payload), encoding="utf-8")
    git(repository, "add", AUTH)
    git(repository, "commit", "-m", "compatibility counterexample")
    result = resolve_reentry(repository, "HEAD")
    assert result.route == ("PENDING_REVIEW" if group == "non_candidate" else "STOP")
    assert result.execution_allowed is False


@pytest.mark.parametrize("status", ["HUMAN_DECISION_REQUIRED", "COMPLETED_PENDING_REVIEW",
                                     "REVIEW_PENDING", "STOP", "BLOCKED", "ACCEPTED", "CLOSED", "UNKNOWN"])
def test_ic01_non_candidate_states(repository: Path, status: str) -> None:
    before = git(repository, "branch", "--list")
    for path in (CURRENT, WORK):
        change(repository, path, "status", status)
    # 缺少整個 candidate-only authority 文件也不能造成 non-candidate crash。
    git(repository, "rm", AUTH, QUOTA, ELIGIBILITY, PACKAGE, DEPENDENCY)
    git(repository, "commit", "-m", "non candidate without deep documents")
    head = git(repository, "rev-parse", "HEAD")
    result = resolve_reentry(repository, "HEAD", status_only=True)
    assert result.route == ("PENDING_REVIEW" if status in ("COMPLETED_PENDING_REVIEW", "REVIEW_PENDING") else "STOP")
    assert result.execution_allowed is False
    assert result.next_action == "REPORT_CURRENT_STATE_WITHOUT_EXECUTION"
    assert git(repository, "rev-parse", "HEAD") == head
    assert git(repository, "branch", "--list") == before
    assert git(repository, "status", "--porcelain") == b""


def test_ic01_actual_consumed_current_no_deep_dereference() -> None:
    result = resolve_reentry(ROOT, "HEAD", status_only=True)
    assert result.route == "STOP"
    assert result.stop_reason == "AUTHORIZATION_NOT_AVAILABLE"
    assert result.execution_allowed is False


def test_ic01_conflicting_status_stops(repository: Path) -> None:
    change(repository, CURRENT, "status", "CLOSED")
    result = resolve_reentry(repository, "HEAD")
    assert result.route == "STOP" and result.stop_reason == "CONFLICTING_WORK_STATUS"
