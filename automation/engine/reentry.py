"""唯讀 unified re-entry snapshot；route 是交接建議，不是 claim/dispatch 授權。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from types import MappingProxyType
from typing import Mapping

from automation.engine.contracts import _freeze_yaml_value
from automation.engine.manifest import (
    ManifestIntegrityError, ManifestVerification, parse_mapping, read_git_blob,
    resolve_commit, verify_manifest,
)


@dataclass(frozen=True)
class ReentrySnapshot:
    """同一 SHA 的最低必要上下文；不自動升級執行或變更 governance。"""
    source_head_sha: str
    manifest: ManifestVerification
    current_state: Mapping[str, str]
    documents: Mapping[str, object]
    route: str
    next_action: str
    stop_reason: str | None
    execution_allowed: bool = False


def _current_projection(text: str) -> Mapping[str, str]:
    """只讀 canonical snapshot 第一個 text fence，避免歷史 NEXT 覆寫 CURRENT。"""
    marker = "### CURRENT_AUTHORITY_SNAPSHOT"
    if marker not in text:
        raise ManifestIntegrityError("canonical CURRENT snapshot missing")
    match = re.search(r"```text\s*\n(.*?)```", text.split(marker, 1)[1], re.S)
    if match is None:
        raise ManifestIntegrityError("canonical CURRENT fence missing")
    state: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        if "=" not in line:
            raise ManifestIntegrityError("invalid CURRENT projection line")
        key, value = (part.strip() for part in line.split("=", 1))
        if not key or not value or key in state:
            raise ManifestIntegrityError("ambiguous CURRENT projection")
        state[key] = value
    if state.get("branch") != "master":
        raise ManifestIntegrityError("authoritative branch must be master")
    return MappingProxyType(state)


def resolve_reentry(
    repo: str | Path, revision: str, *, status_only: bool = False,
    handoff_paths: tuple[str, ...] = (),
) -> ReentrySnapshot:
    """讀 exact repository pointers，不 fetch、不寫檔、不詢問 repo 已有答案。

    open handoff/result/review/STOP 由 caller 提供 exact paths，避免全 repo 掃描。
    完整 executor gates 與 single-use claim 仍由 executor fresh revalidate。
    """
    sha = resolve_commit(repo, revision)
    documents: dict[str, object] = {}

    def text(path: str) -> str:
        value = read_git_blob(repo, sha, path).decode("utf-8")
        documents[path] = value
        return value

    def mapping(path: str) -> dict[str, object]:
        value = parse_mapping(read_git_blob(repo, sha, path))
        documents[path] = value
        return value

    text("AGENTS.md")
    state = _current_projection(text("docs/CURRENT_STATE.md"))
    verification = verify_manifest(repo, sha)
    manifest = mapping(verification.manifest_path)
    for policy in manifest["policies"].values():
        mapping(policy["path"])
    text("docs/CURRENT_WORK.md")
    handoffs = [mapping(path) for path in handoff_paths]
    current = mapping("automation/work_orders/CURRENT_CODEX.yaml")
    text("automation/work_orders/CURRENT_CODEX_TASK.md")
    work = mapping(current["work_order_path"])
    auth = mapping(current["authorization_path"])
    quota = mapping(current["quota_amendment"]["path"])
    eligibility = mapping(current["eligibility_path"])
    package = mapping(auth["package_binding"]["path"])
    dependency = mapping(auth["program_binding"]["dependency_closure_path"])

    reason = None
    if not verification.valid:
        reason = "MANIFEST_INTEGRITY_MISMATCH"
    else:
        for key in ("work_order_id", "package_id", "package_revision", "authorization_id", "authorization_revision", "exact_write_scope", "execution_branch"):
            if current.get(key) != work.get(key) or key not in current:
                reason = "CURRENT_WORK_ORDER_BINDING_MISMATCH"
                break
        binding = auth["exact_binding"]
        quota_binding = quota["exact_binding"]
        if (auth.get("authorization_id") != current.get("authorization_id")
                or auth.get("authorization_revision") != current.get("authorization_revision")
                or binding.get("work_package_id") != current.get("package_id")
                or binding.get("work_package_revision") != current.get("package_revision")
                or package.get("work_package_id") != current.get("package_id")
                or package.get("work_package_revision") != current.get("package_revision")
                or package.get("planned_write_scope") != current.get("exact_write_scope")
                or auth["package_binding"].get("planned_write_scope") != current.get("exact_write_scope")
                or state.get("development_automation_current_package") != current.get("package_id")
                or state.get("development_automation_current_authorization_id") != current.get("authorization_id")):
            reason = reason or "EXACT_AUTHORITY_BINDING_MISMATCH"
        for key in ("work_order_id", "package_id", "package_revision"):
            if quota_binding.get(key) != current.get(key):
                reason = reason or "AMENDMENT_ELIGIBILITY_BINDING_MISMATCH"
        for key in ("work_order_id", "package_id"):
            if eligibility.get(key) != current.get(key):
                reason = reason or "AMENDMENT_ELIGIBILITY_BINDING_MISMATCH"
        if (quota_binding.get("base_authorization_id") != auth.get("authorization_id")
                or quota_binding.get("base_authorization_revision") != auth.get("authorization_revision")
                or eligibility.get("authorization_id") != auth.get("authorization_id")):
            reason = reason or "AMENDMENT_AUTHORIZATION_BINDING_MISMATCH"

    statuses = [doc.get("status") for doc in handoffs] + [current.get("status"), work.get("status")]
    if reason:
        route, action = "STOP", "RESOLVE_GOVERNANCE_INTEGRITY_OR_BINDING"
    elif any(s in ("STOP", "STOPPED", "HARD_BLOCK", "BLOCKED") for s in statuses):
        route, action, reason = "STOP", "RESOLVE_REPOSITORY_STOP", "OPEN_STOP_OR_BLOCKER"
    elif any(s in ("COMPLETED_PENDING_REVIEW", "PENDING_REVIEW", "RESULT_READY", "IMPLEMENTED_PENDING_REVIEW") for s in statuses):
        route, action = "PENDING_REVIEW", "ROUTE_DURABLE_RESULT_TO_WORK"
    elif (auth.get("authorization_state") != "AUTHORIZED"
            or state.get("development_automation_current_authorization_state") != "AUTHORIZED"):
        route, action, reason = "STOP", "RESOLVE_CURRENT_AUTHORIZATION", "AUTHORIZATION_NOT_AVAILABLE"
    elif dependency.get("status") != "ACCEPTED_MATERIALIZED":
        route, action, reason = "WAIT", "WAIT_FOR_DEPENDENCY_CLOSURE", "DEPENDENCY_NOT_ACCEPTED"
    elif (quota.get("status") != "AUTHORIZED_EFFECTIVE"
            or eligibility.get("status") != "ELIGIBLE_FOR_MANUAL_TRIGGER"):
        route, action, reason = "WAIT", "FRESH_ELIGIBILITY_RESOLUTION", "ELIGIBILITY_NOT_READY"
    elif current.get("status") == work.get("status") == "READY_FOR_CODEX" and current.get("handoff_ready") is True:
        route, action = "CODEX_EXECUTION_CANDIDATE", "FRESH_EXECUTOR_GATES_AND_SINGLE_USE_CLAIM_REQUIRED"
    else:
        route, action, reason = "STOP", "RESOLVE_CURRENT_WORK", "NO_LEGAL_READY_WORK"
    if status_only:
        action = "REPORT_CURRENT_STATE_WITHOUT_EXECUTION"
    return ReentrySnapshot(
        sha, verification, state, _freeze_yaml_value(documents), route, action, reason,
    )
