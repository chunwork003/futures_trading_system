"""從指定 Git commit 的原始 blob 核對 manifest；不使用工作樹換行或授權施工。"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Mapping

import yaml

from automation.engine.contracts import MasterManifest
from automation.engine.yaml_io import _UniqueKeySafeLoader


class ManifestIntegrityError(ValueError):
    """Commit、路徑、文件或摘要無法驗證時 fail closed。"""


def _git(repo: str | Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, check=False,
    )
    if result.returncode:
        raise ManifestIntegrityError("Git object cannot be resolved")
    return result.stdout


def resolve_commit(repo: str | Path, revision: str) -> str:
    """先固定 exact commit；後續所有讀取使用此 SHA，避免 ref 移動混合證據。"""
    if not isinstance(revision, str) or not revision or revision.startswith("-"):
        raise ManifestIntegrityError("invalid revision")
    sha = _git(repo, "rev-parse", "--verify", "--end-of-options", revision + "^{commit}").decode().strip()
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", sha):
        raise ManifestIntegrityError("invalid commit identity")
    return sha


def read_git_blob(repo: str | Path, commit_sha: str, path: str) -> bytes:
    """只接受 repository 相對路徑與 exact commit；symlink/tree 不屬文件 blob。"""
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit_sha):
        raise ManifestIntegrityError("exact commit SHA required")
    if (not isinstance(path, str) or not path or "\\" in path or ":" in path
            or path.startswith("/") or any(p in ("", ".", "..") for p in path.split("/"))):
        raise ManifestIntegrityError("invalid repository-relative path")
    if str(PurePosixPath(path)) != path:
        raise ManifestIntegrityError("noncanonical path")
    entry = _git(repo, "ls-tree", "-z", commit_sha, "--", path).split(b"\0")
    if len(entry) != 2 or not entry[0]:
        raise ManifestIntegrityError("missing or ambiguous blob")
    metadata, actual_path = entry[0].split(b"\t", 1)
    mode, kind, oid = metadata.split()
    if actual_path.decode("utf-8") != path or mode not in (b"100644", b"100755") or kind != b"blob":
        raise ManifestIntegrityError("regular file blob required")
    return _git(repo, "cat-file", "blob", oid.decode("ascii"))


def parse_mapping(blob: bytes) -> dict[str, object]:
    """沿用已接受的 safe/unique-key YAML 邊界；JSON 亦為 YAML 子集合。"""
    try:
        value = yaml.load(blob.decode("utf-8"), Loader=_UniqueKeySafeLoader)
    except (UnicodeError, yaml.YAMLError) as exc:
        raise ManifestIntegrityError("invalid safe mapping document") from exc
    if not isinstance(value, dict) or any(not isinstance(k, str) for k in value):
        raise ManifestIntegrityError("string-key mapping required")
    return value


@dataclass(frozen=True)
class HashCheck:
    """保留 manifest 指定值與 Git blob 實測值，供 reviewer 追溯。"""
    field: str
    path: str
    expected: str
    actual: str

    @property
    def matches(self) -> bool:
        return self.expected == self.actual


@dataclass(frozen=True)
class ManifestVerification:
    commit_sha: str
    manifest_path: str
    manifest_sha256: str
    checks: tuple[HashCheck, ...]

    @property
    def valid(self) -> bool:
        return bool(self.checks) and all(item.matches for item in self.checks)


def _references(section: Mapping[str, object], prefix: str = ""):
    for key, value in section.items():
        field = prefix + key
        if isinstance(value, Mapping):
            yield from _references(value, field + ".")
        elif key == "sha256" or key.endswith("_sha256"):
            path_key = "path" if key == "sha256" else key[:-7] + "_path"
            path = section.get(path_key)
            if not isinstance(path, str) or not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ManifestIntegrityError("invalid hash/path binding: " + field)
            yield field, path, value


def verify_manifest(
    repo: str | Path, revision: str,
    manifest_path: str = "automation/governance/master_manifest.v1.yaml",
) -> ManifestVerification:
    """核對同一 exact commit 的全部 hash/path 引用；不推測歷史核對 commit。

    不符摘要以 valid=False 回傳；缺文件、未知輸入契約則明確拋錯。
    previous_sha256 等無 path 的 provenance metadata 不是 hash 引用。
    """
    sha = resolve_commit(repo, revision)
    blob = read_git_blob(repo, sha, manifest_path)
    mapping = parse_mapping(blob)
    try:
        manifest = MasterManifest.model_validate(mapping)
    except ValueError as exc:
        raise ManifestIntegrityError("invalid manifest contract") from exc
    integrity = manifest.hash_integrity
    if (integrity.get("algorithm") != "SHA-256"
            or integrity.get("canonical_input") != "git_blob_bytes"
            or integrity.get("verification_scope") != "exact_review_commit"
            or integrity.get("worktree_bytes_are_authoritative") is not False
            or integrity.get("line_ending_normalization") != "none"):
        raise ManifestIntegrityError("unsupported hash integrity semantics")
    # materialization 區塊只有 provenance；其 previous hash 不代表 current path。
    references = dict(mapping)
    references["agent_reentry"] = {k: v for k, v in mapping["agent_reentry"].items() if k != "materialization"}
    checks = tuple(
        HashCheck(field, path, expected, hashlib.sha256(read_git_blob(repo, sha, path)).hexdigest())
        for field, path, expected in _references(references)
    )
    if not checks:
        raise ManifestIntegrityError("manifest has no hash references")
    return ManifestVerification(sha, manifest_path, hashlib.sha256(blob).hexdigest(), checks)
