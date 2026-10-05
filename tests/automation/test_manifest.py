from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess

import pytest
import yaml

from automation.engine.manifest import (
    ManifestIntegrityError, parse_mapping, read_git_blob, resolve_commit, verify_manifest,
)


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = "automation/governance/master_manifest.v1.yaml"


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.PIPE)


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-b", "master")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    git(tmp_path, "config", "user.name", "Fixture")
    git(tmp_path, "config", "core.autocrlf", "false")
    manifest = yaml.safe_load(git(ROOT, "show", "HEAD:" + MANIFEST))
    paths = {MANIFEST}

    def collect(section):
        for key, value in section.items():
            if isinstance(value, dict):
                collect(value)
            elif key == "path" or key.endswith("_path"):
                paths.add(value)

    collect(manifest)
    for path in paths:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(git(ROOT, "show", "HEAD:" + path))
    git(tmp_path, "add", "--", *sorted(paths))
    git(tmp_path, "commit", "-m", "fixture")
    return tmp_path


def test_exact_git_blob_integrity(repository: Path) -> None:
    result = verify_manifest(repository, "HEAD")
    assert result.valid
    assert len(result.checks) == 13
    assert all(check.matches for check in result.checks)
    assert result.commit_sha == resolve_commit(repository, "HEAD")


def test_crlf_worktree_is_not_authority(repository: Path) -> None:
    sha = resolve_commit(repository, "HEAD")
    path = repository / "AGENTS.md"
    blob = read_git_blob(repository, sha, "AGENTS.md")
    assert b"\r\n" not in blob
    path.write_bytes(blob.replace(b"\n", b"\r\n"))
    result = verify_manifest(repository, sha)
    check = next(item for item in result.checks if item.path == "AGENTS.md")
    assert result.valid
    assert check.actual != hashlib.sha256(path.read_bytes()).hexdigest()


def test_review_commit_remains_pinned_after_new_commit(repository: Path) -> None:
    sha = resolve_commit(repository, "HEAD")
    (repository / "AGENTS.md").write_bytes(b"changed\n")
    git(repository, "add", "AGENTS.md")
    git(repository, "commit", "-m", "change navigation")
    assert verify_manifest(repository, sha).valid
    changed = verify_manifest(repository, "HEAD")
    assert not changed.valid
    assert [c.path for c in changed.checks if not c.matches] == ["AGENTS.md"]


def test_missing_blob_fails_closed(repository: Path) -> None:
    git(repository, "rm", "AGENTS.md")
    git(repository, "commit", "-m", "missing navigation")
    with pytest.raises(ManifestIntegrityError):
        verify_manifest(repository, "HEAD")


@pytest.mark.parametrize("path", ["../AGENTS.md", "/AGENTS.md", "C:/AGENTS.md", "a\\b", "a//b", "./AGENTS.md"])
def test_invalid_paths_rejected(repository: Path, path: str) -> None:
    with pytest.raises(ManifestIntegrityError):
        read_git_blob(repository, resolve_commit(repository, "HEAD"), path)


@pytest.mark.parametrize("revision", ["--help", "missing-commit", ""])
def test_invalid_revision_rejected(repository: Path, revision: str) -> None:
    with pytest.raises(ManifestIntegrityError):
        resolve_commit(repository, revision)


@pytest.mark.parametrize("blob", [b"a: 1\na: 2\n", b"!!python/object:builtins.object {}", b"[]", b"\xff"])
def test_unsafe_or_ambiguous_mapping_rejected(blob: bytes) -> None:
    with pytest.raises(ManifestIntegrityError):
        parse_mapping(blob)


def test_unsupported_integrity_semantics_rejected(repository: Path) -> None:
    path = repository / MANIFEST
    path.write_text(path.read_text(encoding="utf-8").replace("git_blob_bytes", "worktree_bytes"), encoding="utf-8")
    git(repository, "add", MANIFEST)
    git(repository, "commit", "-m", "unsupported integrity")
    with pytest.raises(ManifestIntegrityError, match="semantics"):
        verify_manifest(repository, "HEAD")
