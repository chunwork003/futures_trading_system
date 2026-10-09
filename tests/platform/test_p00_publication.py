"""Publication精確快照、父鏈、raw bytes與不可逆動作界線。"""
import hashlib
import json
from pathlib import Path

import pytest

from scripts.p00_publication import build_manifest, BRANCH
from test_p00_context import git, write, commit


@pytest.fixture
def publication(tmp_path):
    git(tmp_path, "init", "-q", "-b", "master")
    git(tmp_path, "config", "user.name", "Fixture")
    git(tmp_path, "config", "user.email", "fixture@example.invalid")
    git(tmp_path, "config", "core.autocrlf", "false")
    git(tmp_path, "remote", "add", "origin", "https://github.com/chunwork003/futures_trading_system.git")
    write(tmp_path, "docs/program/p00_status.v1.json", {"current_checkpoint_evidence": "docs/program/checkpoints/fixture.json"})
    write(tmp_path, "docs/program/checkpoints/fixture.json", {"targeted_tests": "NOT_RUN_FIXTURE_ONLY", "full_platform_tests": "NOT_RUN_FIXTURE_ONLY"})
    write(tmp_path, "docs/program/delete.md", "delete")
    write(tmp_path, "docs/program/change.md", "before")
    write(tmp_path, "trading/protected.py", "accepted")
    base = commit(tmp_path)
    git(tmp_path, "update-ref", "refs/remotes/origin/master", base)
    git(tmp_path, "update-ref", "refs/remotes/origin/" + BRANCH, base)
    git(tmp_path, "checkout", "-qb", BRANCH)
    write(tmp_path, "docs/program/change.md", "after")
    (tmp_path / "docs/program/delete.md").unlink()
    (tmp_path / "docs/program/raw.md").write_bytes(b"a\r\nb\r\n")
    head = commit(tmp_path)
    return tmp_path, base, head


def test_precise_parent_chain_adm_and_raw_content_hashes(publication):
    root, base, head = publication
    m = build_manifest(root, head, base, base)
    assert m["local_head"] == head and m["expected_remote_head"] == base
    assert m["commits"][0]["parents"] == [base]
    assert m["net_status_counts"] == {"A": 1, "D": 1, "M": 1}
    raw = next(r for r in m["files"] if r["path"].endswith("raw.md"))
    assert raw["after"]["content_sha256"] == hashlib.sha256(b"a\r\nb\r\n").hexdigest()
    assert m["ordinary_fast_forward"] is True
    assert m["publication_effects"]["REMOTE_PUBLISHED"] is False
    assert m["publication_effects"]["ACCEPTED"] is False
    assert m["publication_effects"]["product_authorization"] == "NOT_AUTHORIZED"
    assert m["push_refspec_if_exactly_approved"] == head + ":refs/heads/" + BRANCH


def test_protected_change_then_revert_cannot_hide_inside_ancestry(publication):
    root, base, head = publication
    write(root, "trading/protected.py", "changed")
    commit(root)
    write(root, "trading/protected.py", "accepted")
    head = commit(root)
    with pytest.raises(ValueError, match="PROTECTED_SCOPE_CHANGE"):
        build_manifest(root, head, base, base)


@pytest.mark.parametrize("failure", ["branch", "head", "remote", "repository", "master"])
def test_stale_or_wrong_destination_cannot_get_manifest(publication, failure):
    root, base, head = publication
    expected, master = base, base
    if failure == "branch": git(root, "checkout", "-qb", "wrong")
    if failure == "head": head = base
    if failure == "remote": expected = head
    if failure == "repository": git(root, "remote", "set-url", "origin", "https://github.com/other/other.git")
    if failure == "master": master = head
    with pytest.raises(ValueError): build_manifest(root, head, expected, master)


def test_uncommitted_authoring_is_exactly_excluded_not_silently_published(publication):
    root, base, head = publication
    write(root, "docs/program/change.md", "not yet committed")
    m = build_manifest(root, head, base, base)
    assert m["uncommitted_worktree_changes_excluded_from_payload"] == [" M docs/program/change.md"]
    assert next(r for r in m["files"] if r["path"].endswith("change.md"))["after"]["content_sha256"] == hashlib.sha256(b"after").hexdigest()
    write(root, "trading/protected.py", "uncommitted violation")
    with pytest.raises(ValueError): build_manifest(root, head, base, base)
