from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
import subprocess

import pytest
import yaml

from automation.engine.manifest import ManifestIntegrityError
from automation.engine.reentry import resolve_reentry


ROOT = Path(__file__).resolve().parents[2]
CURRENT = "automation/work_orders/CURRENT_CODEX.yaml"
WORK = "automation/work_orders/WO-AUTO-IMP-002-01.yaml"
AUTH = "automation/authorizations/AUTH-AUTO-IMP-002-01.v1.yaml"
STATE = "docs/CURRENT_STATE.md"


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.PIPE)


@pytest.fixture
def repository(tmp_path: Path) -> Path:
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
